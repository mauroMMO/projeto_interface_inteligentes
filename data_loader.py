import csv
import os
from dataclasses import dataclass
from io import StringIO
from typing import Iterator, List, Set, Tuple


@dataclass
class TableData:
	rows: List[dict]
	columns: List[str]

	def copy(self) -> "TableData":
		return TableData(rows=[row.copy() for row in self.rows], columns=self.columns.copy())

	def head(self, count: int) -> "TableData":
		return TableData(rows=self.rows[:count], columns=self.columns.copy())

	def iterrows(self) -> Iterator[Tuple[int, dict]]:
		for index, row in enumerate(self.rows):
			yield index, row

	def to_csv(self, index: bool = False) -> str:
		output = StringIO()
		writer = csv.DictWriter(output, fieldnames=self.columns, extrasaction="ignore", lineterminator="\n")
		writer.writeheader()
		for row in self.rows:
			writer.writerow({column: row.get(column, "") for column in self.columns})
		return output.getvalue()


def _read_csv_file(csv_path: str) -> TableData:
	if not os.path.exists(csv_path):
		raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")

	for encoding in ("utf-8-sig", "latin1"):
		try:
			with open(csv_path, "r", encoding=encoding, newline="") as csv_file:
				reader = csv.DictReader(csv_file)
				if not reader.fieldnames:
					raise ValueError(f"CSV sem cabeçalho válido: {csv_path}")

				raw_columns = [str(column).strip() for column in reader.fieldnames]
				columns = ["ID" if index == 0 and (column == "" or column.startswith("Unnamed")) else column for index, column in enumerate(raw_columns)]
				rows: List[dict] = []

				for raw_row in reader:
					row = {}
					for index, raw_column in enumerate(reader.fieldnames):
						column_name = columns[index]
						value = raw_row.get(raw_column, "")
						row[column_name] = "" if value is None else str(value).strip()
					rows.append(row)

				return TableData(rows=rows, columns=columns)
		except UnicodeDecodeError:
			continue

	raise UnicodeDecodeError("utf-8", b"", 0, 1, f"Não foi possível ler o CSV: {csv_path}")


def _build_table_view_from_questions(df_perguntas: TableData) -> TableData:
	"""Cria a vista tabular usada nas condições sem imagem a partir do CSV único."""
	cols_para_remover = {
		"Resposta esperada (gabarito)",
		"Notas / como avaliar",
		"Gemini G",
		"Gemini GT",
		"Gemini T",
		"Claude G",
		"Claude GT",
		"Claude T",
		"ChatGpt G",
		"ChatGpt GT",
		"ChatGpt T",
	}
	columns = [column for column in df_perguntas.columns if column not in cols_para_remover]
	rows = [{column: row.get(column, "") for column in columns} for row in df_perguntas.rows]
	return TableData(rows=rows, columns=columns)


def load_experiment_data(questions_csv_path: str, data_csv_path: str | None = None):
	"""Carrega o banco de perguntas e a tabela do experimento.

	A condição de tabela deve vir de um CSV próprio, como TABELA.csv.
	"""
	df_perguntas = _read_csv_file(questions_csv_path)
	if not data_csv_path:
		raise ValueError("É necessário informar data_csv_path com a tabela do experimento (ex.: TABELA.csv).")

	if not os.path.exists(data_csv_path):
		raise FileNotFoundError(f"Arquivo da tabela não encontrado: {data_csv_path}")

	if os.path.abspath(data_csv_path) == os.path.abspath(questions_csv_path):
		raise ValueError("data_csv_path não pode apontar para o arquivo de perguntas; use TABELA.csv.")

	df_dados = _read_csv_file(data_csv_path)

	return df_perguntas, df_dados


def get_processed_combinations(output_csv_path: str) -> Set[Tuple[str, str, str]]:
	"""Lê o CSV de resultados e devolve as combinações já processadas."""
	if not os.path.exists(output_csv_path):
		return set()

	with open(output_csv_path, "r", encoding="utf-8-sig", newline="") as csv_file:
		reader = csv.DictReader(csv_file)
		required_columns = {"Modelo", "Condicao", "ID_Pergunta"}

		if not reader.fieldnames or not required_columns.issubset(set(reader.fieldnames)):
			return set()

		processed_set: Set[Tuple[str, str, str]] = set()
		for row in reader:
			processed_set.add((str(row.get("Modelo", "")), str(row.get("Condicao", "")), str(row.get("ID_Pergunta", ""))))

		return processed_set


def save_result_incremental(output_csv_path: str, result_dict: dict) -> None:
	"""Anexa um resultado ao CSV, criando o arquivo quando necessário."""
	output_dir = os.path.dirname(output_csv_path)
	if output_dir:
		os.makedirs(output_dir, exist_ok=True)

	file_exists = os.path.exists(output_csv_path)
	with open(output_csv_path, "a", encoding="utf-8-sig", newline="") as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=list(result_dict.keys()), extrasaction="ignore")
		if not file_exists:
			writer.writeheader()
		writer.writerow(result_dict)