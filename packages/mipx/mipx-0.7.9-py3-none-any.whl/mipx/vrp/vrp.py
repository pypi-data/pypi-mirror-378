# -*- coding: utf-8 -*-
# @Time    : 2025/08/22 14:50:17
# @Author  : luyi
# @Desc    : 车辆路径相关的算法
from typing import Callable, List, Optional, Union
from ortools.constraint_solver import pywrapcp

from .extra import (
    VrpAssignment,
    VrpRoutingDimension,
    VrpRoutingSearchParameters,
    VrpVar,
)


class Vrp:
    def __init__(
        self,
        num_node: int,
        num_vehicles: int,
        start_nodes: Union[List[int], int],
        end_nodes: Optional[Union[List[int], int]] = None,
    ) -> None:
        if not isinstance(start_nodes, list):
            start_nodes = [start_nodes for _ in range(num_vehicles)]
        if end_nodes is None:
            end_nodes = start_nodes
        if not isinstance(end_nodes, list):
            end_nodes = [end_nodes for _ in range(num_vehicles)]

        self.__manager = pywrapcp.RoutingIndexManager(
            num_node, num_vehicles, start_nodes, end_nodes
        )
        self.__routing = pywrapcp.RoutingModel(self.__manager)
        self.__routing.vehicles()
        # ---------------------
        self._set_dimension = set()

    def numVehicles(self) -> int:
        """获取车辆数量"""
        return self.__routing.vehicles()

    def routingStart(self, vehicle: int) -> int:
        """获取车辆的起始节点索引"""
        return self.__routing.Start(vehicle)

    def routingEnd(self, vehicle: int) -> int:
        """获取车辆的终点节点索引"""
        return self.__routing.End(vehicle)

    def routingIsEnd(self, index: int) -> bool:
        """判断车辆的节点索引是否是终点"""
        return self.__routing.IsEnd(index)

    def routingNextVar(self, index: int) -> VrpVar:
        """获取车辆的下一个节点变量"""
        return VrpVar(self.__routing.NextVar(index))

    def routingVehicleVar(self, index: int) -> VrpVar:
        return VrpVar(self.__routing.VehicleVar(index))

    def fixedDurationIntervalVar(self, var: VrpVar, duration: int, name: str):
        solver: pywrapcp.Solver = self.__routing.solver()
        a = solver.FixedDurationIntervalVar(var.IntVar, duration, name)
        print(type(a))

    def indexToNode(self, index: int) -> int:
        """将索引转换为节点编号"""
        return self.__manager.IndexToNode(index)

    def getArcCostForVehicle(self, from_index: int, to_index: int, vehicle: int) -> int:
        """获取车辆从from_index到to_index的边的成本"""
        return self.__routing.GetArcCostForVehicle(from_index, to_index, vehicle)

    def nodeToIndex(self, node: int) -> int:
        """将节点编号转换为索引"""
        return self.__manager.NodeToIndex(node)

    def addPickupAndDelivery(self, pickup_index: int, delivery_index: int):
        """添加车辆的取货和送货节点"""
        self.__routing.AddPickupAndDelivery(pickup_index, delivery_index)

    def addConstr(self, expr):
        solver: pywrapcp.Solver = self.__routing.solver()
        solver.Add(expr)

    def setArcCostEvaluatorOfAllVehicles(
        self, arc_cost_callback: Callable[[int, int], int]
    ):
        """设置所有车辆的边成本计算器"""
        self.__routing.SetArcCostEvaluatorOfAllVehicles(
            self.__routing.RegisterTransitCallback(arc_cost_callback)
        )

    def addVariableMinimizedByFinalizer(self, var: VrpVar):
        """
        将一个变量添加到解的最终确定器中用于最小化。
        解的最终确定器在每次搜索过程中找到一个解时都会被调用，可用于实例化次要变量（例如维度的累计变量）。

        :param var: 变量
        """
        self.__routing.AddVariableMinimizedByFinalizer(var.IntVar)

    def addDimension(
        self,
        evaluator_callback: Callable[[int, int], int],
        slack_max: int,
        capacity: Union[List[int], int],
        fix_start_cumul_to_zero: bool,
        name: str,
    ) -> VrpRoutingDimension:
        """
        模型创建
        用于向路径添加维度的方法；维度表示沿路径在各个节点上累积的量。
        这些量可以是路径上承载的重量、体积，或距离、时间等。

        节点处的量由“cumul”变量表示，而节点之间的量的变化（增加或减少）由“transit”变量表示。
        这些变量之间的关系如下：
            如果 j == next(i)，则 cumul(j) = cumul(i) + transit(i, j) + slack(i)
        其中 slack 是一个非负的松弛变量（例如在时间维度中可表示等待时间）。
        将 fix_start_cumul_to_zero 设为 True 时，会强制所有车辆起点节点的“cumul”变量值等于0。
        该方法创建一个维度，其中 transit 变量被约束为等于 evaluator(i, next(i))；
        'slack_max' 是松弛变量的上界，'capacity' 是 cumul 变量的上界。
        'name' 是引用该维度所使用的名称；该名称用于从路由模型中获取 cumul和transit 变量。

        :param evaluator_callback: 边成本计算器
        :param slack_max: 用于表示等待的变量的最大值
        :param capacity: 每条路线累计的总数量上限
        :param fix_start_cumul_to_zero: 布尔值。如果为true，则累积值从0开始。在大多数情况下，应将其设置为 True
        :param name: 维度名称
        """
        assert name not in self._set_dimension, f"维度名称{name}重复"
        self._set_dimension.add(name)
        self.__routing.AddDimension(
            self.__routing.RegisterTransitCallback(evaluator_callback),
            slack_max,
            capacity,
            fix_start_cumul_to_zero,
            name,
        )
        return self.getDimension(name)

    def addDimensionWithVehicleCapacity(
        self,
        evaluator_callback: Callable[[int], int],
        slack_max: int,
        vehicle_capacity: Union[List[int], int],
        fix_start_cumul_to_zero: bool,
        name: str,
    ):
        self.__routing.AddDimensionWithVehicleCapacity(
            self.__routing.RegisterUnaryTransitCallback(evaluator_callback),
            slack_max,
            vehicle_capacity,
            fix_start_cumul_to_zero,
            name,
        )
        return self.getDimension(name)

    def getDimension(self, name: str) -> VrpRoutingDimension:
        di = self.__routing.GetDimensionOrDie(name)
        return VrpRoutingDimension(di)

    def DefaultRoutingSearchParameters(self) -> VrpRoutingSearchParameters:
        return VrpRoutingSearchParameters()

    def solveWithParameters(
        self, search_parameters: VrpRoutingSearchParameters, solutions=None
    ) -> Optional[VrpAssignment]:

        solution = self.__routing.SolveWithParameters(
            search_parameters._to_or_parameter(), solutions
        )
        if solution is None:
            return None
        return VrpAssignment(solution)

    @property
    def Params(self):
        pass

    def optimize(self):
        pass
