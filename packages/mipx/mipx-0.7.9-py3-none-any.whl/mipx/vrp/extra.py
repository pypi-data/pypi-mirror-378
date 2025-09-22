from enum import Enum
from ortools.constraint_solver import (
    routing_enums_pb2,
    pywrapcp,
    routing_parameters_pb2,
)


class VrpFirstSolutionStrategy(Enum):
    UNSET = routing_enums_pb2.FirstSolutionStrategy.UNSET
    """
    未设置。使用 AUTOMATIC 代替。
    """

    AUTOMATIC = routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC
    """
    让求解器根据模型自动选择最合适的策略。
    推荐在不确定时使用。
    """

    PATH_CHEAPEST_ARC = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    """
    从起点出发，每次都选择代价最小的弧（边）来扩展路径。
    类似贪心算法：每次选当前最便宜的下一个节点。
    速度快，常作为默认选择。
    """

    PATH_MOST_CONSTRAINED_ARC = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_MOST_CONSTRAINED_ARC
    )
    """
    与 PATH_CHEAPEST_ARC 类似，但优先选择约束最多的弧（如时间窗更紧的边）。
    适合有复杂约束（如时间窗）的问题。
    """

    EVALUATOR_STRATEGY = routing_enums_pb2.FirstSolutionStrategy.EVALUATOR_STRATEGY
    """
    与 PATH_CHEAPEST_ARC 类似，但弧的成本由用户通过 RoutingModel::SetFirstSolutionEvaluator() 
    设置的自定义函数来评估。
    """

    SAVINGS = routing_enums_pb2.FirstSolutionStrategy.SAVINGS
    """
    使用 Clarke & Wright 节约算法。
    经典 VRP 启发式：先为每个客户单独派车，然后合并能“节约”最多成本的路线。
    适合标准车辆路径问题（VRP）。
    """

    PARALLEL_SAVINGS = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_SAVINGS
    """
    SAVINGS 算法的并行版本。
    不再顺序构建单条路线，而是并行考虑多个可能的合并，能更快地构建多条路线。
    """

    SWEEP = routing_enums_pb2.FirstSolutionStrategy.SWEEP
    """
    扫掠算法（Wren & Holliday）。
    将所有客户点按极角排序，然后按顺序分组分配给车辆。
    适合二维平面上分布的问题。
    """

    CHRISTOFIDES = routing_enums_pb2.FirstSolutionStrategy.CHRISTOFIDES
    """
    Christofides 算法的变种（使用最大匹配而非最大权匹配）。
    用于旅行商问题（TSP），通过逐步扩展路径来构建解。
    在度量空间 TSP 中有理论近似保证。
    """

    ALL_UNPERFORMED = routing_enums_pb2.FirstSolutionStrategy.ALL_UNPERFORMED
    """
    将所有节点都标记为“不执行”（不访问）。
    只有在节点是可选的（即属于带有有限惩罚的不相交约束）时才能找到可行解。
    """

    BEST_INSERTION = routing_enums_pb2.FirstSolutionStrategy.BEST_INSERTION
    """
    迭代地将每个节点插入到全局成本函数下“最划算”的位置。
    基于整个模型的总成本评估插入代价。
    目前仅适用于包含可选节点的模型。
    """

    PARALLEL_CHEAPEST_INSERTION = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    )
    """
    迭代地将“插入成本最低”的节点插入其最佳位置。
    成本基于弧成本函数（而非全局成本）。
    多条路径并行构建，比 BEST_INSERTION 更快。
    """

    SEQUENTIAL_CHEAPEST_INSERTION = (
        routing_enums_pb2.FirstSolutionStrategy.SEQUENTIAL_CHEAPEST_INSERTION
    )
    """
    顺序构建路线：为每辆车依次构建完整路径。
    对每条路线，不断将最便宜的节点插入其最佳位置，直到无法再插入。
    比 PARALLEL_CHEAPEST_INSERTION 更快。
    """

    LOCAL_CHEAPEST_INSERTION = (
        routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_INSERTION
    )
    """
    迭代地将每个节点插入其最便宜的位置。
    与 PARALLEL_CHEAPEST_INSERTION 不同，它优先插入离路径起点/终点最远的节点。
    比 SEQUENTIAL_CHEAPEST_INSERTION 更快。
    """

    LOCAL_CHEAPEST_COST_INSERTION = (
        routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_COST_INSERTION
    )
    """
    与 LOCAL_CHEAPEST_INSERTION 相同，但插入成本基于整个路由模型的成本函数，
    而不仅仅是弧的成本。考虑了更多因素（如时间、载重等）。
    """

    GLOBAL_CHEAPEST_ARC = routing_enums_pb2.FirstSolutionStrategy.GLOBAL_CHEAPEST_ARC
    """
    变量基础启发式。
    每次选择整个图中成本最低的弧（边），连接两个节点。
    类似于最小生成树的思想。
    """

    LOCAL_CHEAPEST_ARC = routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_ARC
    """
    选择第一个尚未确定后继的节点，然后将其连接到能产生最便宜弧的节点。
    局部贪心策略。
    """

    FIRST_UNBOUND_MIN_VALUE = (
        routing_enums_pb2.FirstSolutionStrategy.FIRST_UNBOUND_MIN_VALUE
    )
    """
    选择第一个尚未确定后继的节点，并将其连接到第一个可用的节点。
    这相当于选择第一个未绑定变量并赋予其最小可能值的策略。
    """


class VrpLocalSearchMetaheuristic(Enum):
    UNSET = routing_enums_pb2.LocalSearchMetaheuristic.UNSET
    """
    未设置。使用 AUTOMATIC 代替。
    """
    AUTOMATIC = routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC
    """
    让求解器根据模型自动选择最合适的策略。
    推荐在不确定时使用。
    """
    GREEDY_DESCENT = routing_enums_pb2.LocalSearchMetaheuristic.GREEDY_DESCENT
    """
    贪婪（随机）搜索算法。
    随机选择一些节点，并将其固定在一定的位置，以期望产生更好的结果。
    适用于小型模型。
    """
    GUIDED_LOCAL_SEARCH = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    """
    基于指导的局部搜索算法。
    随机选择一些节点，并将其固定在一定的位置，以期望产生更好的结果。
    适用于小型模型。
    """
    SIMULATED_ANNEALING = routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING
    """
    基于模拟退火的局部搜索算法。
    随机选择一些节点，并将其固定在一定的位置，以期望产生更好的结果。
    适用于大型模型。
    """
    TABU_SEARCH = routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH
    """
    基于 Tabu 启发式的局部搜索算法。
    随机选择一些节点，并将其固定在一定的位置，以期望产生更好的结果。
    适用于大型模型。
    """
    GENERIC_TABU_SEARCH = routing_enums_pb2.LocalSearchMetaheuristic.GENERIC_TABU_SEARCH
    """
    通用 Tabu 启发式的局部搜索算法。
    随机选择一些节点，并将其固定在一定的位置，以期望产生更好的结果。
    适用于大型模型。
    """


class VrpRoutingSearchParameters:
    def __init__(self):
        self.__or_parameters: routing_parameters_pb2.RoutingSearchParameters = (
            pywrapcp.DefaultRoutingSearchParameters()
        )

    def setFirstSolutionStrategy(self, strategy: VrpFirstSolutionStrategy):
        self.__or_parameters.first_solution_strategy = strategy.value

    def setLocalSearchMetaheuristic(self, metaheuristic: VrpLocalSearchMetaheuristic):
        self.__or_parameters.local_search_metaheuristic = metaheuristic.value

    def setTimeLimit(self, time_limit_seconds: int):
        self.__or_parameters.time_limit.FromSeconds(time_limit_seconds)

    def _to_or_parameter(self):
        return self.__or_parameters


class VrpIntervalVar:
    def __init__(self, interval_var: pywrapcp.IntervalVar) -> None:
        self.__interval_var = interval_var

    @property
    def IntervalVar(self):
        return self.__interval_var


class VrpVar:
    def __init__(self, var: pywrapcp.IntVar) -> None:
        self.__var = var

    @property
    def IntVar(self):
        return self.__var

    def setRange(self, lb: int, ub: int):
        self.__var.SetRange(lb, ub)

    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, VrpVar):
            return self.__var == value.__var
        else:
            return False

    def __ge__(self, value: object, /) -> bool:
        if isinstance(value, VrpVar):
            return self.__var >= value.__var
        else:
            return False

    def __gt__(self, value: object, /) -> bool:
        if isinstance(value, VrpVar):
            return self.__var > value.__var
        else:
            return False

    def __le__(self, value: object, /) -> bool:
        if isinstance(value, VrpVar):
            return self.__var <= value.__var
        else:
            return False

    def __lt__(self, value: object, /) -> bool:
        if isinstance(value, VrpVar):
            return self.__var < value.__var
        else:
            return False

    def __ne__(self, value: object, /) -> bool:
        if isinstance(value, VrpVar):
            return self.__var != value.__var
        else:
            return True


class VrpRoutingDimension:
    def __init__(self, di: pywrapcp.RoutingDimension) -> None:
        self.__di = di

    def setGlobalSpanCostCoefficient(self, coefficient: int):
        """
        设置一个与全局维度跨度成比例的成本，即路径结束累计变量的最大值与路径开始累计变量的最小值之间的差值。
        换句话说：
        全局跨度成本 =
        系数 * (维度结束值的最大值 - 维度开始值的最小值)。
        """
        self.__di.SetGlobalSpanCostCoefficient(coefficient)

    def cumulVar(self, index: int) -> VrpVar:
        """
        获取累计变量。
        """
        return VrpVar(self.__di.CumulVar(index))


class VrpAssignment:
    def __init__(self, solution: pywrapcp.Assignment) -> None:
        self.__solution = solution

    def objectiveValue(self):
        """
        获取目标函数值。
        """
        return self.__solution.ObjectiveValue()

    def value(self, var: VrpVar):
        """
        获取变量的值。
        """
        return self.__solution.Value(var.IntVar)

    def min(self, var: VrpVar):
        """
        获取变量的最小值。
        """
        return self.__solution.Min(var.IntVar)

    def max(self, var: VrpVar):
        """
        获取变量的最大值。
        """
        return self.__solution.Max(var.IntVar)
