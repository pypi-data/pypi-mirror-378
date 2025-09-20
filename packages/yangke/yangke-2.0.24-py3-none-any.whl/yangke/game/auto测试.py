from auto import (ConditionalTask, TaskCondition, TaskStep, ConditionType, CompositeCondition, ConditionOperator,
                  FailureHandling, ExecutionAction, ExecutionMethod, InputInterface)

task = ConditionalTask()

# 定义任务步骤
tasks = [
    TaskStep(
        name="检查游戏状态",
        execution_conditions=[],  # 无执行条件，总是执行
        execution_method=None,  # 无执行动作
        expected_results=CompositeCondition(
            conditions=[
                TaskCondition(
                    condition_type=ConditionType.IMAGE_EXISTS,
                    value="game_window.png"
                ),
                TaskCondition(
                    condition_type=ConditionType.TEXT_EXISTS,
                    value="HP:"
                )
            ],
            operator=ConditionOperator.AND
        ),
        timeout=5,
        failure_handling=FailureHandling.RAISE_ERROR,
        next_step_on_success="查找敌人",
        next_step_on_failure="启动游戏"
    ),
    TaskStep(
        name="启动游戏",
        execution_conditions=[],  # 无执行条件
        execution_method=ExecutionMethod(
            action=ExecutionAction.DOUBLE_CLICK,
            target="game_icon.png"
        ),
        expected_results=TaskCondition(
            condition_type=ConditionType.IMAGE_EXISTS,
            value="game_window.png"
        ),
        timeout=30,
        failure_handling=FailureHandling.RAISE_ERROR,
        next_step_on_success="查找敌人",
        next_step_on_failure="启动游戏"  # 失败时重试
    ),
    TaskStep(
        name="查找敌人",
        execution_conditions=[
            CompositeCondition(
                conditions=[
                    TaskCondition(
                        condition_type=ConditionType.IMAGE_EXISTS,
                        value="player_character.png"
                    ),
                    CompositeCondition(
                        conditions=[
                            TaskCondition(
                                condition_type=ConditionType.IMAGE_EXISTS,
                                value="enemy_normal.png"
                            ),
                            TaskCondition(
                                condition_type=ConditionType.IMAGE_EXISTS,
                                value="enemy_elite.png"
                            )
                        ],
                        operator=ConditionOperator.OR
                    )
                ],
                operator=ConditionOperator.AND
            )
        ],
        execution_method=ExecutionMethod(
            action=ExecutionAction.LEFT_CLICK,
            target="attack_button.png"
        ),
        expected_results=TaskCondition(
            condition_type=ConditionType.IMAGE_EXISTS,
            value="enemy_health_bar.png"
        ),
        timeout=5,
        failure_handling=FailureHandling.WAIT_AND_RETRY,
        wait_time=1,
        next_step_on_success="判断敌人的类型",
        next_step_on_failure="等待敌人"
    ),
    TaskStep(
        name="判断敌人的类型",
        execution_conditions=[
            TaskCondition(
                condition_type=ConditionType.IMAGE_EXISTS,
                value="enemy_health_bar.png"
            )
        ],
        execution_method=None,  # 无执行动作，仅用于判断
        expected_results=None,
        timeout=1,
        failure_handling=FailureHandling.RAISE_ERROR,
        next_step_conditions={
            "释放AOE技能": TaskCondition(
                condition_type=ConditionType.IMAGE_EXISTS,
                value="enemy_multiple.png"
            ),
            "释放单体技能": CompositeCondition(
                conditions=[
                    TaskCondition(
                        condition_type=ConditionType.IMAGE_EXISTS,
                        value="enemy_single.png"
                    ),
                    TaskCondition(
                        condition_type=ConditionType.IMAGE_NOT_EXISTS,
                        value="enemy_multiple.png"
                    )
                ],
                operator=ConditionOperator.AND
            )
        }
    ),
    TaskStep(
        name="释放AOE技能",
        execution_conditions=[
            TaskCondition(
                condition_type=ConditionType.IMAGE_EXISTS,
                value="enemy_health_bar.png"
            )
        ],
        execution_method=ExecutionMethod(
            action=ExecutionAction.KEY_PRESS,
            key="2"  # AOE技能键
        ),
        expected_results=TaskCondition(
            condition_type=ConditionType.IMAGE_NOT_EXISTS,
            value="enemy_health_bar.png"
        ),
        timeout=10,
        failure_handling=FailureHandling.WAIT_AND_RETRY,
        wait_time=1,
        next_step_on_success="查找敌人",
        next_step_on_failure="查找敌人"
    ),
    TaskStep(
        name="释放单体技能",
        execution_conditions=[
            TaskCondition(
                condition_type=ConditionType.IMAGE_EXISTS,
                value="enemy_health_bar.png"
            )
        ],
        execution_method=ExecutionMethod(
            action=ExecutionAction.KEY_PRESS,
            key="1"  # 单体技能键
        ),
        expected_results=TaskCondition(
            condition_type=ConditionType.IMAGE_NOT_EXISTS,
            value="enemy_health_bar.png"
        ),
        timeout=10,
        failure_handling=FailureHandling.WAIT_AND_RETRY,
        wait_time=1,
        next_step_on_success="查找敌人",
        next_step_on_failure="查找敌人"
    ),
    TaskStep(
        name="等待敌人",
        execution_conditions=[],  # 无执行条件
        execution_method=ExecutionMethod(
            action=ExecutionAction.WAIT,
            target="5"  # 等待5秒
        ),
        expected_results=None,
        timeout=5,
        failure_handling=FailureHandling.RAISE_ERROR,
        next_step_on_success="查找敌人",
        next_step_on_failure="查找敌人"
    )
]


class Op(InputInterface):
    def __init__(self):
        ...

    def key_down(self, key: str):
        ...

    def key_up(self, key: str):
        ...

    def left_click(self, x: int, y: int):
        ...

    def move_to(self, x: int, y: int):
        ...

    def press_key(self, key: str):
        ...

    def right_click(self, x: int, y: int):
        ...


# 定义任务
task.define_tasks(tasks)
task.set_input_interface(Op())
# 执行任务
task.run_with_interruption_handling()
