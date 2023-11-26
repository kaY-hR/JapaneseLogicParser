import inspect, itertools
from inspect import Parameter
from tools import print_return
from functools import lru_cache
from collections import defaultdict

class KnowledgeBase:
    def __init__(self):
        """
        KnowledgeBaseクラスの初期化メソッド。
        基本要素、関係、関係の説明、事実の回答を格納するためのリストと辞書を初期化する。
        """
        self.atoms = []  # 基本要素を格納するリスト
        self.facts = {}  # 事実の名前と関数
        self.rules = {}  # ルールの名前と関数
        self.relation_explanations = {}  # 関係の説明を格納する辞書
        self.fact_answers = {}  # 事実の回答を格納する辞書
        self.find_solution_mode = False
        self.stacked_args = defaultdict(list)  # 無限再帰回避のため、再帰で検索する場合は既に検索済みの引数を記録する

    def define_fact(self, name, answers=None, explanation=None):
        """
        事実を定義する

        Args:
            name (str): 事実の名前。
            answers (list of tuple, optional): 事実に対する回答のリスト。デフォルトはNone。
            explanation (str, optional): 事実の説明。デフォルトはNone。
        """

        if answers:
            # 固有名詞一覧に固有名詞を登録
            for args in answers:
                for arg in args:
                    if arg not in self.atoms:
                        self.atoms.append(arg)

            # 事実が成立する固有名詞を登録
            if name not in self.fact_answers:
                self.fact_answers[name] = []
            self.fact_answers[name] += answers

            # 事実の真偽を返す関数を登録
            self.facts[name] = lambda *args: args in self.fact_answers[name]
        else:
            self.facts[name] = lambda: True

        if explanation:
            self.relation_explanations[name] = explanation

    def define_rule(self, name, rule, explanation=None):
        """
        ルールを定義する

        Args:
            name (str): ルールの名前。
            rule (function): ルールを定義する関数。
            explanation (str, optional): ルールの説明。デフォルトはNone。
        """

        # positinal変数はPrologにおける変数である
        # 変数の数を数えて、固有名詞の組合せを生成し、総当たりで検討する関数を登録する
        fixed_arg_count = sum(1 for param in inspect.signature(rule).parameters.values() if param.kind == Parameter.POSITIONAL_OR_KEYWORD)
        
        if fixed_arg_count == 1:
            self.rules[name] = lambda *args: any(rule(X, *args) for X in self.atoms)
        else:
            atom_combinations = list(itertools.combinations_with_replacement(self.atoms, fixed_arg_count))
            self.rules[name] = lambda *args: any(rule(*variables, *args) for variables in atom_combinations)

        if explanation:
            self.relation_explanations[name] = explanation

    def define_rule_from_func(self, name, func, explanation=None):
        self.rules[name] = func
        if explanation:
            self.relation_explanations[name] = explanation

    def define(self, name: str, *args):
        """
        事実またはルールを定義する

        Args:
            name (str): 定義する事実またはルールの名前。
            args: 事実またはルールに関連する引数。
        """
        if len(args) == 1 and callable(args[0]) and args[0].__name__ == "<lambda>":
            self.define_rule(name=name, rule=args[0])
        else:
            self.define_fact(name=name, answers=[tuple(args)])

    @print_return()
    def explain(self, name: str):
        """
        関係の説明を返す。論理演算には無関係。

        Args:
            name (str): 説明を取得したい関係の名前。

        Returns:
            str: 関係の説明。定義されていない場合は、それを示すメッセージを返す。
        """
        if name in self.relation_explanations:
            return self.relation_explanations[name]
        else:
            return f"Explanation for {name} is not defined."

    def set_explanation(self, name: str, explanation: str):
        """
        explain関数で返却する説明を設定する。論理演算には無関係。

        Args:
            name (str): 説明を設定したい関係の名前。
            explanation (str): 設定する説明。
        """
        self.relation_explanations[name] = explanation

    @print_return(lambda result, *args, **kwargs: str(result) + " satisfies.")
    def find_solution(self, requirement):
        """
        要件を満たす解を探索する

        Args:
            requirement (function): 解が満たすべき要件を定義する関数。

        Returns:
            list: 要件を満たす解のリスト。
        """
        self.find_solution_mode = True
        self.stacked_args = defaultdict(list)
        requirement_arg_count = len(inspect.signature(requirement).parameters)
        result = None
        if requirement_arg_count == 1:
            answer_candidates = self.atoms.copy()
            result = [answer for answer in answer_candidates if requirement(answer)]
        else:
            answer_candidates = list(itertools.combinations_with_replacement(self.atoms, requirement_arg_count))
            result = [answer for answer in answer_candidates if requirement(*answer)]

        self.stacked_args = defaultdict(list)
        self.find_solution_mode = False
        return result

    @lru_cache()
    @print_return(lambda result, *args, **kwargs: args[0] + (" in " + "-".join(args[1:]) if args[1:] else "") + " is " + str(result))
    def check(self, relation_name, *args):
        # 既に評価された関係と引数の組み合わせを追跡するセット

        # 事実に定義されていればTrue
        if relation_name in self.facts:
            if self.facts[relation_name](*args):
                return True

        # ルールに定義されていれば、再帰的に評価
        if relation_name in self.rules:
            # if relation_name in self.stacked_args:
            #     return False
            # self.stacked_args[relation_name] = args
            return self.rules[relation_name](*args)

        return False
