from multiprocessing.managers import DictProxy
from typing import Dict, List


def is_dead(father_process_dag: "DictProxy[str, List[str]]") -> bool:
    try:
        with father_process_dag._mutex:
            dead = (
                len([v for v in dict(father_process_dag).values() if "error" not in v])
                <= 1
            )
        return dead
    except (KeyError, OSError, ConnectionError, EOFError, BrokenPipeError) as e:
        # En cas d'erreur d'accès au DAG (spawn), considérer comme vivant pour éviter arrêt prématuré
        print(f"Warning: Error accessing DAG, assuming alive: {e}")
        return False


def is_finished_with_errors(father_process_dag: "DictProxy[str, List[str]]") -> bool:
    try:
        with father_process_dag._mutex:
            has_errors = (
                len([v for v in dict(father_process_dag).values() if "error" in v]) >= 1
            )
        dead = is_dead(father_process_dag)

        killme = dead and has_errors
        if killme:
            print("Pipeline has errors and will be closed")
        return killme
    except (KeyError, OSError, ConnectionError, EOFError, BrokenPipeError) as e:
        # En cas d'erreur d'accès au DAG (spawn), considérer comme pas fini pour éviter arrêt prématuré
        print(f"Warning: Error accessing DAG, assuming not finished: {e}")
        return False


def register_father_son(
    father_process_dag: "DictProxy[str, List[str]]", father: str, son: str
):
    try:
        with father_process_dag._mutex:
            dag: Dict[str, List[str]] = father_process_dag._getvalue()
            if father not in dag:
                father_process_dag[father] = [son]
            else:
                father_process_dag[father] = [
                    *dag[father],
                    son,
                ]
    except (KeyError, OSError, ConnectionError, EOFError, BrokenPipeError) as e:
        # DAG temporairement inaccessible - reporter l'enregistrement
        print(f"Warning: DAG temporarily inaccessible, skipping registration: {e}")
        # Ne pas crash - les processus doivent pouvoir démarrer même si DAG inaccessible
        pass


def format_node_name(node: str) -> str:
    import psutil

    try:
        p = psutil.Process(int(node))
        return f"({node}) {p.name()}"
    except Exception:
        return node


def make_dot_graph(debug_graph: str, father_process_dag: "DictProxy[str, List[str]]"):
    try:
        from graphviz import Digraph  # type: ignore
    except ImportError:
        print("Warning: graphviz not available, skipping debug graph generation")
        return None

    try:
        dot = Digraph("G", filename=debug_graph, format="png")

        with father_process_dag._mutex:
            for node, parents in father_process_dag.items():
                dot.node(node, format_node_name(node))

                for parent in parents:
                    if parent not in father_process_dag:
                        dot.node(parent, parent)

                    if parent:
                        dot.edge(parent, node)

        return dot
    except Exception as e:
        print(f"Warning: Could not generate debug graph: {e}")
        return None
