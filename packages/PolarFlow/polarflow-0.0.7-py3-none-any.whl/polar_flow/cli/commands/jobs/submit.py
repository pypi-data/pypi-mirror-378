from typing import TYPE_CHECKING

import typer

from polar_flow._vendor.slurm_client.models.v0043_job_desc_msg_kill_warning_flags_item import (
    V0043JobDescMsgKillWarningFlagsItem as MsgKillWarningFlags,
)
from polar_flow._vendor.slurm_client.models.v0043_job_desc_msg_open_mode_item import (
    V0043JobDescMsgOpenModeItem,
)
from polar_flow._vendor.slurm_client.models.v0043_job_desc_msg_shared_item import (
    V0043JobDescMsgSharedItem,
)
from polar_flow._vendor.slurm_client.models.v0043_job_submit_req import V0043JobSubmitReq
from polar_flow.cli.client import SlurmClient
from polar_flow.cli.commands.jobs.read_toml_script import job_desc_from_toml
from polar_flow.cli.commands.jobs.utils import parse_noval_ui32, parse_noval_ui64, parse_time_type
from polar_flow.cli.printers import (
    PrintProgress,
    print_client_we,
    print_debug,
    print_json_ex,
)

from .ann import submit_ann
from .jobs import job_app

if TYPE_CHECKING:
    from polar_flow.cli.config import AppConfig


@job_app.command("submit")
def job_submit(  # noqa: PLR0913
    ctx: typer.Context,
    account: str | None = typer.Option(None, help="与作业关联的账户"),
    argv: list[str] = typer.Option(
        None,
        help="脚本的参数。注意：总是用创建的脚本文件的路径覆盖argv[0]。如果使用了这个选项，argv[0]应该是一个一次性值。",
        show_default=False,
    ),
    begin_time: str | None = typer.Option(
        None,
        help="将作业的分配延迟到指定的时间 UNIX时间戳或时间字符串 '[MM/DD[/YY]-]HH:MM[:SS]' 或者 'infinite'",
    ),
    cpus_per_tres: str | None = typer.Option(
        None,
        help="以分号分隔的 TRES=# 列表，表示每个指定 TRES 分配的 CPU 数量（目前仅用于 gres/gpu）",
    ),
    deadline: str | None = typer.Option(
        None,
        help="作业最晚可开始的时间（UNIX 时间戳或 Slurm 识别的时间字符串，如 '[MM/DD[/YY]-]HH:MM[:SS]'）",
    ),
    dependency: str | None = typer.Option(None, help="在本作业开始前必须满足条件的其他作业"),
    end_time: str | None = typer.Option(
        None,
        help="预期结束时间（UNIX 时间戳或时间字符串，如 '[MM/DD[/YY]-]HH:MM[:SS]'）",
    ),
    environment: list[str] = typer.Option(None, help="要为作业设置的环境变量", show_default=False),
    group_id: str | None = typer.Option(None, help="作业所属用户的组 ID"),
    immediate: bool | None = typer.Option(None, help="若为 True，则在指定时间内资源不可用时退出"),
    job_id: int | None = typer.Option(None, help="作业 ID"),
    kill_on_node_fail: bool | None = typer.Option(None, help="若为 True，当节点故障时杀死作业"),
    memory_per_tres: str | None = typer.Option(
        None,
        help="以分号分隔的 TRES=# 列表，表示每个指定 TRES 分配的内存（MB）（目前仅用于 gres/gpu）",
    ),
    name: str | None = typer.Option(None, help="作业名称"),
    tasks: int | None = typer.Option(None, help="任务数量"),
    open_mode: list[V0043JobDescMsgOpenModeItem] | None = typer.Option(
        None,
        help="stdout/stderr 文件的打开模式",
        show_default=False,
    ),
    partition: str | None = typer.Option(None, help="作业所属分区"),
    hold: bool | None = typer.Option(None, help="暂停 (true) or 继续 (false) 任务"),
    priority: int | None = typer.Option(None, help="任务优先级"),
    qos: str | None = typer.Option(None, help="作业分配的 QoS（暂无，都是默认 Qos）"),
    requeue: bool | None = typer.Option(None, help="是否允许作业被重新排队"),
    script: str = typer.Argument(help="作业批处理脚本 *.toml"),
    shared: list[V0043JobDescMsgSharedItem] | None = typer.Option(
        None,
        help="作业与其他作业共享资源的方式（如允许）",
        show_default=False,
    ),
    time_limit: int | None = typer.Option(None, help="最大运行时间，单位为分钟，整数"),
    time_minimum: int | None = typer.Option(None, help="最小运行时间，单位为分钟，整数"),
    tres_per_job: str | None = typer.Option(
        None,
        help="每个作业分配的 TRES=# 列表，目前只用于 gres/gpu，比如 gres/gpu=1",
    ),
    tres_per_task: str | None = typer.Option(
        None,
        help="每个任务分配的 TRES=# 列表（逗号分隔），目前只用于 gres/gpu，比如 gres/gpu=1",
    ),
    user_id: str | None = typer.Option(None, help="作业所属用户的 UID"),
    kill_warning_flags: list[MsgKillWarningFlags] | None = typer.Option(
        None,
        help="与作业信号相关的标志，用于区分需要接受哪些信号",
        show_default=False,
    ),
    kill_warning_signal: str | None = typer.Option(
        None,
        help='接近结束时间时发送的信号（如 "10" 或 "USR1"）',
    ),
    current_working_directory: str = typer.Option(
        None,
        "--chdir",
        help="作业使用的工作目录",
    ),
    cpus_per_task: int | None = typer.Option(None, help="每个任务需要的 CPU 数"),
    minimum_cpus: int | None = typer.Option(None, help="所需 CPU 最小值"),
    maximum_cpus: int | None = typer.Option(None, help="所需 CPU 最大值"),
    ntasks_per_tres: int | None = typer.Option(None, help="可访问每个 GPU 的任务数"),
    memory_per_cpu: int | None = typer.Option(None, help="每个 CPU 分配的内存"),
    temporary_disk_per_node: int | None = typer.Option(None, help="每节点所需的最小临时磁盘空间"),
    standard_error: str | None = typer.Option(None, help="stderr 文件路径"),
    standard_input: str | None = typer.Option(None, help="stdin 文件路径"),
    standard_output: str | None = typer.Option(None, help="stdout 文件路径"),
    # account_gather_frequency: int | None = typer.Option(
    #     None,
    #     help="作业计费与性能采样的间隔（秒）",
    # ),
    # flags: None | list[V0043JobDescMsgFlagsItem] = typer.Option(
    #     None,
    #     help="作业标志",
    #     show_default=False,
    # ),
    # tres_per_node: str | None = typer.Option(None, help="每个节点分配的 TRES=# 列表（逗号分隔）"),
    # tres_per_socket: str | None = typer.Option(None, help="每个插槽分配的 TRES=# 列表（逗号分隔）"),
    # memory_per_node: int | None = typer.Option(None, help="每个 节点 分配的内存"),
    # minimum_cpus_per_node: int | None = typer.Option(None, help="每节点最少 CPU 数"),
    # minimum_boards_per_node: int | None = typer.Option(None, help="每节点所需的板卡数"),
    # minimum_sockets_per_board: int | None = typer.Option(None, help="每板所需插槽数"),
    # sockets_per_node: int | None = typer.Option(None, help="每节点所需插槽数"),
    # threads_per_core: int | None = typer.Option(None, help="每核心所需线程数"),
    # tasks_per_node: int | None = typer.Option(None, help="每个节点启动的任务数"),
    # tasks_per_socket: int | None = typer.Option(None, help="每个插槽启动的任务数"),
    # tasks_per_core: int | None = typer.Option(None, help="每个核心启动的任务数"),
    # tasks_per_board: int | None = typer.Option(None, help="每块板卡启动的任务数"),
    # admin_comment: str | None = typer.Option(None, help="管理员填写的任意备注"),
    # allocation_node_list: str | None = typer.Option(None, help="执行资源分配的本地节点"),
    # allocation_node_port: int | None = typer.Option(None, help="用于发送分配确认的端口"),
    # array: str | None = typer.Option(None, help="作业数组索引值规范"),
    # batch_features: str | None = typer.Option(None, help="批处理脚本节点所需的特性"),
    # burst_buffer: str | None = typer.Option(None, help="突发缓冲区配置"),
    # clusters: str | None = typer.Option(None, help="联合作业可运行的集群"),
    # cluster_constraint: str | None = typer.Option(None, help="联合集群接受同级作业所需具备的特性"),
    # comment: str | None = typer.Option(None, help="用户填写的任意备注"),
    # contiguous: bool | None = typer.Option(None, help="若需要连续节点则为 True"),
    # container: str | None = typer.Option(None, help="OCI 容器包的绝对路径"),
    # container_id: str | None = typer.Option(None, help="OCI 容器 ID"),
    # core_specification: int | None = typer.Option(None, help="专用核心数量"),
    # thread_specification: int | None = typer.Option(None, help="专用线程数量"),
    # cpu_binding: str | None = typer.Option(None, help="将任务绑定到已分配 CPU 的方法"),
    # cpu_binding_flags: list[V0043JobDescMsgCpuBindingFlagsItem] | None = typer.Option(
    #     None,
    #     help="CPU 绑定相关标志",
    #     show_default=False,
    # ),
    # cpu_frequency: str | None = typer.Option(None, help="请求的 CPU 频率范围 <p1>[-p2][:p3]"),
    # crontab: str | None = typer.Option(None, help="定时任务"),
    # delay_boot: int | None = typer.Option(
    #     None,
    #     help="在作业满足可开始条件后，为满足特性要求而延迟重启节点的秒数",
    # ),
    # rlimits: str | None = typer.Option(None, help=""),
    # excluded_nodes: list[str] = typer.Option(None, help="", show_default=False),
    # extra: str | None = typer.Option(None, help="启用额外约束时用于节点筛选的任意字符串"),
    # constraints: str | None = typer.Option(None, help="必需特性的逗号分隔列表"),
    # hetjob_group: int | None = typer.Option(None, help="应用于此异构作业组件的唯一序号"),
    # licenses: str | None = typer.Option(None, help="作业所需的许可证"),
    # mail_type: list[V0043JobDescMsgMailTypeItem] | None = typer.Option(
    #     None,
    #     help="邮件事件类型",
    #     show_default=False,
    # ),
    # mail_user: str | None = typer.Option(None, help="接收邮件通知的用户"),
    # mcs_label: str | None = typer.Option(None, help="作业上的多类别安全（MCS）标签"),
    # memory_binding: str | None = typer.Option(None, help="用于 map/mask_cpu 的绑定映射"),
    # memory_binding_type: list[V0043JobDescMsgMemoryBindingTypeItem] | None = typer.Option(
    #     None,
    #     help="任务与内存的绑定方法",
    #     show_default=False,
    # ),
    # network: str | None = typer.Option(None, help="作业步骤的网络规格"),
    # nice: int | None = typer.Option(None, help="请求的作业优先级变更"),
    # oom_kill_step: int | None = typer.Option(None, help="若某任务发生 OOM 则终止整个步骤"),
    # reserve_ports: int | None = typer.Option(None, help="发送各类通知消息的端口"),
    # overcommit: bool | None = typer.Option(None, help="超量分配资源"),
    # distribution_plane_size: str | None = typer.Option(None, help="", hidden=True),
    # power_flags: list[str] = typer.Option(None, help="", show_default=False),
    # prefer: str | None = typer.Option(None, help="偏好但非必需的特性（逗号分隔）"),
    # profile: list[V0043JobDescMsgProfileItem] | None = typer.Option(
    #     None,
    #     help="acct_gather_profile 插件使用的剖析配置",
    #     show_default=False,
    # ),
    # reboot: bool | None = typer.Option(None, help="开始前请求节点重启"),
    # required_nodes: list[str] = typer.Option(None, help="", show_default=False),
    # reservation: str | None = typer.Option(None, help="要使用的保留资源名称"),
    # site_factor: int | None = typer.Option(None, help="站点自定义优先级因子"),
    # spank_environment: list[str] = typer.Option(None, help="", show_default=False),
    # distribution: str | None = typer.Option(None, help="布局"),
    # tres_bind: str | None = typer.Option(None, help="任务到 TRES 的绑定指令"),
    # tres_freq: str | None = typer.Option(None, help="TRES 频率指令"),
    # wait_all_nodes: bool | None = typer.Option(None, help="若为 True，则等待所有节点启动后再开始"),
    # kill_warning_delay: str | None = typer.Option(None, help=""),
    # nodes: str | None = typer.Option(None, help="节点数量范围规范（如 1-15:4）"),
    # minimum_nodes: int | None = typer.Option(None, help="最小节点数"),
    # maximum_nodes: int | None = typer.Option(None, help="最大节点数"),
    # selinux_context: str | None = typer.Option(None, help="SELinux 上下文"),
    # required_switches: str | None = typer.Option(None, help=""),
    # segment_size: str | None = typer.Option(None, help=""),
    # wait_for_switch: int | None = typer.Option(None, help="等待交换机的最长时间（秒）"),
    # wckey: str | None = typer.Option(None, help="工作负载特征键"),
    # x11: list[str] = typer.Option(None, help="X11 转发选项", show_default=False),
    # x11_magic_cookie: str | None = typer.Option(None, help="X11 转发的魔术 cookie"),
    # x11_target_host: str | None = typer.Option(
    #     None,
    #     help="当 x11_target_port=0 时为主机名或 UNIX 套接字",
    # ),
    # x11_target_port: int | None = typer.Option(None, help="TCP 端口"),
) -> None:
    """提交自动作业脚本"""
    with PrintProgress():
        try:
            job = job_desc_from_toml(script)
        except ValueError as ve:
            raise typer.BadParameter(f"解析脚本文件出错: {ve}") from ve
        except FileNotFoundError as fe:
            raise typer.BadParameter(f"解析脚本文件出错: {fe}") from fe
        except RuntimeError as re:
            raise typer.BadParameter(f"解析脚本文件出错: {re}") from re

        if account is not None:
            job.account = account
        if argv is not None:
            job.argv = argv
        if cpus_per_tres is not None:
            job.cpus_per_tres = cpus_per_tres
        if begin_time is not None:
            job.begin_time = parse_time_type(begin_time)
        if deadline is not None:
            job.deadline = parse_time_type(deadline).number
        if dependency is not None:
            job.dependency = dependency
        if end_time is not None:
            job.end_time = parse_time_type(end_time).number

        if environment is not None:
            job.environment = environment
        if not job.environment:
            job.environment = ["_THERE_MUST_BE_A_ENV_VAR_=THIS_IS_A_BUG"]

        if group_id is not None:
            job.group_id = group_id
        if immediate is not None:
            job.immediate = immediate
        if job_id is not None:
            job.job_id = job_id
        if kill_on_node_fail is not None:
            job.kill_on_node_fail = kill_on_node_fail
        if memory_per_tres is not None:
            job.memory_per_tres = memory_per_tres
        if name is not None:
            job.name = name
        if tasks is not None:
            job.tasks = tasks
        if open_mode is not None:
            job.open_mode = open_mode
        if partition is not None:
            job.partition = partition
        if hold is not None:
            job.hold = hold
        if priority is not None:
            job.priority = parse_noval_ui32(str(priority))
        if qos is not None:
            job.qos = qos
        if requeue is not None:
            job.requeue = requeue
        if shared is not None:
            job.shared = shared
        if time_limit is not None:
            job.time_limit = parse_noval_ui32(str(time_limit))
        if time_minimum is not None:
            job.time_minimum = parse_noval_ui32(str(time_minimum))
        if tres_per_job is not None:
            job.tres_per_job = tres_per_job
        if tres_per_task is not None:
            job.tres_per_task = tres_per_task
        if user_id is not None:
            job.user_id = user_id
        if kill_warning_flags is not None:
            job.kill_warning_flags = kill_warning_flags
        if kill_warning_signal is not None:
            job.kill_warning_signal = kill_warning_signal

        if current_working_directory is not None:
            job.current_working_directory = current_working_directory
        if not job.current_working_directory:
            raise typer.BadParameter("请指定工作目录 --chdir 或 'current_working_directory'")

        if cpus_per_task is not None:
            job.cpus_per_task = cpus_per_task
        if minimum_cpus is not None:
            job.minimum_cpus = minimum_cpus
        if maximum_cpus is not None:
            job.maximum_cpus = maximum_cpus

        # 默认所有 task 共享 GPU
        if ntasks_per_tres is not None:
            job.ntasks_per_tres = ntasks_per_tres
        if not job.ntasks_per_tres:
            job.ntasks_per_tres = job.tasks

        if memory_per_cpu is not None:
            job.memory_per_cpu = parse_noval_ui64(str(memory_per_cpu))
        if temporary_disk_per_node is not None:
            job.temporary_disk_per_node = temporary_disk_per_node
        if standard_error is not None:
            job.standard_error = standard_error
        if standard_input is not None:
            job.standard_input = standard_input
        if standard_output is not None:
            job.standard_output = standard_output

        if not job.script:
            raise typer.BadParameter("脚本中未包含 'script'")

        cfg: AppConfig = ctx.obj["cfg"]
        token: str = ctx.obj["token"]
        debug: bool = ctx.obj["debug"]

        print_debug(str(job.to_dict()), title="Payload", debug=debug)

        jobs = V0043JobSubmitReq(job=job)

        c = SlurmClient(cfg, token, debug=debug)
        data = c.submit_job(body=jobs)
        errors = data.errors
        warnings = data.warnings
        print_client_we(warnings=warnings, errors=errors)
        res_job_id = data.job_id
        res_job_submit_user_msg = data.job_submit_user_msg
        res_step_id = data.step_id

        if type(res_job_id) is not int:
            res_job_id = None
        if type(res_job_submit_user_msg) is not str:
            res_job_submit_user_msg = None
        if type(res_step_id) is not str:
            res_step_id = None

    print_json_ex(
        "操作结果",
        data={
            "result": {
                "job_id": res_job_id,
                "step_id": res_step_id,
                "job_submit_user_msg": res_job_submit_user_msg,
            },
        },
        key_priority=["result"],
        expand=True,
        show_raw=debug,
        annotations=submit_ann,
        show_side_notes_for_tables=True,
        show_side_notes_for_dicts=True,
        dict_notes_min_hits=2,
        dict_notes_max_depth=3,
    )
