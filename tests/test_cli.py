import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)

        self.dados = Path(self.pasta.name) / "artistas.json"
        artistas = [
            {"id": "a", "nome": "Queen", "generos": ["rock"]},
            {"id": "b", "nome": "Rock", "generos": ["rock"]},
        ]

        self.dados.write_text(
            json.dumps(artistas),
            encoding="utf-8",
        )

    def executar(self, *argumentos):
        return subprocess.run(
            [
                sys.executable,
                str(RAIZ / "main.py"),
                "--dados",
                str(self.dados),
                *argumentos,
            ],
            cwd=RAIZ,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_ordena_antes_de_aplicar_limite(self):
        for busca in ("sequencial", "binaria"):
            with self.subTest(busca=busca):
                resultado = self.executar(
                    "--termo", "rock",
                    "--busca", busca,
                    "--limite", "1",
                )

                self.assertEqual(
                    resultado.returncode, 0, resultado.stderr
                )
                self.assertIn("Total encontrado: 2", resultado.stdout)
                self.assertIn("1. Rock | Score: 100", resultado.stdout)
                self.assertNotIn("Queen", resultado.stdout)

    def test_termo_inexistente(self):
        resultado = self.executar("--termo", "xyz_inexistente")

        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Nenhum artista encontrado.", resultado.stdout)

    def test_consulta_vazia_lista_todos(self):
        resultado = self.executar("--termo", "")

        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Total encontrado: 2", resultado.stdout)
        self.assertIn("1. Queen | Score: 0", resultado.stdout)
        self.assertIn("2. Rock | Score: 0", resultado.stdout)

    def test_rejeita_limites_invalidos(self):
        for limite in ("0", "-1", "abc"):
            with self.subTest(limite=limite):
                resultado = self.executar("--limite", limite)
                self.assertNotEqual(resultado.returncode, 0)

    def test_rejeita_busca_invalida(self):
        resultado = self.executar("--busca", "invalida")
        self.assertNotEqual(resultado.returncode, 0)

    def test_arquivo_inexistente(self):
        self.dados.unlink()

        resultado = self.executar()

        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn(
            "Não foi possível carregar os dados",
            resultado.stderr,
        )

    def test_json_invalido(self):
        self.dados.write_text("{invalido", encoding="utf-8")

        resultado = self.executar()

        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn(
            "Não foi possível carregar os dados",
            resultado.stderr,
        )


if __name__ == "__main__":
    unittest.main()

