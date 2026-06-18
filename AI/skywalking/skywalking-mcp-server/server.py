"""
SkyWalking MCP Server - Python 实现 (兼容 SkyWalking 9.x / 10.x)
依赖: pip install mcp httpx
环境变量: SW_URL, SW_USERNAME, SW_PASSWORD
"""
import os, re, json
from datetime import datetime, timedelta, timezone
from typing import Optional
import httpx
from mcp.server.fastmcp import FastMCP

SW_URL = os.environ.get("SW_URL", "https://skywalking.xxx.com")
SW_USERNAME = os.environ.get("SW_USERNAME", "")
SW_PASSWORD = os.environ.get("SW_PASSWORD", "")
GRAPHQL_EP = SW_URL.rstrip("/") + "/graphql"
mcp = FastMCP("skywalking-apm")


# ============ 工具函数 ============

async def gql(query: str, variables: dict = None) -> dict:
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    auth = (SW_USERNAME, SW_PASSWORD) if SW_USERNAME else None
    async with httpx.AsyncClient(verify=False, timeout=30) as c:
        r = await c.post(GRAPHQL_EP, json=payload, auth=auth,
                         headers={"Content-Type": "application/json"})
        r.raise_for_status()
        d = r.json()
        if d.get("errors"):
            raise Exception(json.dumps(d["errors"], ensure_ascii=False))
        return d.get("data", {})


def parse_time(s: str, default=None) -> datetime:
    if not s:
        return default or datetime.now(timezone.utc)
    if s.lower() == "now":
        return datetime.now(timezone.utc)
    m = re.match(r'^-(\d+)([smhd])$', s)
    if m:
        v, u = int(m.group(1)), m.group(2)
        d = {"s": timedelta(seconds=v), "m": timedelta(minutes=v),
             "h": timedelta(hours=v), "d": timedelta(days=v)}[u]
        return datetime.now(timezone.utc) - d
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d %H%M",
                "%Y-%m-%d %H", "%Y-%m-%d"]:
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return default or datetime.now(timezone.utc)


def build_duration(start: str = "", end: str = "", step: str = "") -> dict:
    now = datetime.now(timezone.utc)
    s = parse_time(start, now - timedelta(minutes=30))
    e = parse_time(end, now)
    if not step:
        diff = (e - s).total_seconds()
        if diff >= 7 * 86400:
            step = "DAY"
        elif diff >= 86400:
            step = "HOUR"
        else:
            step = "MINUTE"
    fmt_map = {"DAY": "%Y-%m-%d", "HOUR": "%Y-%m-%d %H",
               "MINUTE": "%Y-%m-%d %H%M", "SECOND": "%Y-%m-%d %H%M%S"}
    fmt = fmt_map.get(step, "%Y-%m-%d %H%M")
    return {"start": s.strftime(fmt), "end": e.strftime(fmt), "step": step}


# ============ MCP Tools ============

@mcp.tool()
async def list_services(layer: str = "GENERAL") -> str:
    """列出指定layer下的所有服务"""
    data = await gql("""query($layer:String!){
        services:listServices(layer:$layer){id name group shortName layers normal}}""",
        {"layer": layer})
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
async def list_instances(service_id: str, start: str = "-1h",
                         end: str = "now", step: str = "") -> str:
    """列出服务的所有实例"""
    dur = build_duration(start, end, step)
    data = await gql("""query($id:ID!,$dur:Duration!){
        instances:listInstances(duration:$dur,serviceId:$id){
        id name language instanceUUID attributes{name value}}}""",
        {"id": service_id, "dur": dur})
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
async def list_endpoints(service_id: str, keyword: str = "",
                         limit: int = 50) -> str:
    """列出服务的端点(接口)，可按keyword过滤"""
    data = await gql("""query($id:ID!,$kw:String!,$limit:Int!){
        pods:findEndpoint(serviceId:$id,keyword:$kw,limit:$limit){
        id value:name label:name}}""",
        {"id": service_id, "kw": keyword, "limit": limit})
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
async def query_traces(service_id: str = "", endpoint_id: str = "",
                       trace_id: str = "", trace_state: str = "ALL",
                       start: str = "-1h", end: str = "now",
                       min_duration: int = 0, max_duration: int = 0,
                       order: str = "BY_START_TIME",
                       page_size: int = 20, page_num: int = 1) -> str:
    """查询链路追踪Trace，支持按服务/端点/状态/耗时过滤"""
    dur = build_duration(start, end)
    paging = {"pageNum": page_num, "pageSize": page_size}

    # 尝试多种 schema 格式以兼容不同 SkyWalking 版本
    # 方案1: SkyWalking 9.2.x schema (queryDuration 在 condition 外部)
    errors = []
    try:
        cond = {"traceState": trace_state, "queryOrder": order, "paging": paging}
        if service_id:
            cond["serviceId"] = service_id
        if endpoint_id:
            cond["endpointId"] = endpoint_id
        if trace_id:
            cond["traceId"] = trace_id
        if min_duration > 0:
            cond["minTraceDuration"] = min_duration
        if max_duration > 0:
            cond["maxTraceDuration"] = max_duration

        data = await gql("""query($cond:TraceQueryCondition!,$dur:Duration!){
            result:queryBasicTraces(duration:$dur,condition:$cond){
            traces{segmentId traceIds endpointNames duration start isError}
            total}}""",
            {"cond": cond, "dur": dur})
        return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        errors.append(f"schema1: {e}")

    # 方案2: queryDuration 在 condition 内部 (9.3+/10.x)
    try:
        cond2 = {"queryDuration": dur, "traceState": trace_state,
                 "queryOrder": order, "paging": paging}
        if service_id:
            cond2["serviceId"] = service_id
        if endpoint_id:
            cond2["endpointId"] = endpoint_id
        if trace_id:
            cond2["traceId"] = trace_id
        if min_duration > 0:
            cond2["minTraceDuration"] = min_duration
        if max_duration > 0:
            cond2["maxTraceDuration"] = max_duration

        data = await gql("""query($cond:TraceQueryCondition!){
            result:queryBasicTraces(condition:$cond){
            traces{segmentId traceIds endpointNames duration start isError}
            total}}""",
            {"cond": cond2})
        return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        errors.append(f"schema2: {e}")

    # 方案3: 9.2 可能用 needTotal 不同或字段名差异
    try:
        cond3 = {"queryDuration": dur, "traceState": trace_state,
                 "queryOrder": order,
                 "paging": {"pageNum": page_num, "pageSize": page_size,
                            "needTotal": True}}
        if service_id:
            cond3["serviceId"] = service_id
        if endpoint_id:
            cond3["endpointId"] = endpoint_id
        if trace_id:
            cond3["traceId"] = trace_id
        if min_duration > 0:
            cond3["minTraceDuration"] = min_duration
        if max_duration > 0:
            cond3["maxTraceDuration"] = max_duration

        data = await gql("""query($cond:TraceQueryCondition!){
            result:queryBasicTraces(condition:$cond){
            traces{segmentId traceIds endpointNames duration start isError}}}""",
            {"cond": cond3})
        return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        errors.append(f"schema3: {e}")

    return json.dumps({"error": "All trace query schemas failed", "details": errors},
                      ensure_ascii=False)


@mcp.tool()
async def query_trace_detail(trace_id: str) -> str:
    """根据traceId查询完整链路详情"""
    data = await gql("""query($id:ID!){trace:queryTrace(traceId:$id){spans{
        traceId segmentId spanId parentSpanId serviceCode serviceInstanceName
        startTime endTime endpointName type peer component isError layer
        tags{key value} logs{time data{key value}}
        refs{traceId parentSegmentId parentSpanId type}}}}""",
        {"id": trace_id})
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
async def execute_mqe(expression: str, service_name: str = "",
                      layer: str = "GENERAL", endpoint_name: str = "",
                      instance_name: str = "",
                      start: str = "-30m", end: str = "now",
                      step: str = "") -> str:
    """执行指标查询(如service_cpm,service_resp_time,service_percentile等)。
    兼容SkyWalking 9.x（无MQE，使用readMetricsValues替代）和10.x（execExpression）。
    expression中如果包含/等运算符，会自动提取指标名并在结果中做后处理。"""
    dur = build_duration(start, end, step)

    # 尝试提取纯指标名（处理类似 service_sla/100 的表达式）
    metric_name = expression.strip()
    divisor = 1
    if "/" in metric_name:
        parts = metric_name.split("/")
        metric_name = parts[0].strip()
        try:
            divisor = float(parts[1].strip())
        except ValueError:
            divisor = 1

    # 确定 scope 和构建 MetricsCondition
    if endpoint_name:
        scope = "Endpoint"
        cond = {"name": metric_name,
                "entity": {"scope": scope, "serviceName": service_name,
                           "endpointName": endpoint_name, "normal": True}}
    elif instance_name:
        scope = "ServiceInstance"
        cond = {"name": metric_name,
                "entity": {"scope": scope, "serviceName": service_name,
                           "serviceInstanceName": instance_name, "normal": True}}
    else:
        scope = "Service"
        cond = {"name": metric_name,
                "entity": {"scope": scope, "serviceName": service_name,
                           "normal": True}}

    # 先尝试 labeled 查询（适用于 service_percentile 等 LABELED_VALUE 指标）
    try:
        data = await gql("""query($dur:Duration!,$labels:[String!]!,$cond:MetricsCondition!){
            result:readLabeledMetricsValues(condition:$cond,labels:$labels,duration:$dur){
            label values{values{value}}}}""",
            {"dur": dur, "labels": ["0", "1", "2", "3", "4"], "cond": cond})
        result = data.get("result", [])
        # 检查是否有有效数据
        has_data = False
        if isinstance(result, list):
            for item in result:
                vals = item.get("values", {}).get("values", [])
                if any(v.get("value", 0) != 0 for v in vals):
                    has_data = True
                    break
        if has_data:
            if divisor != 1:
                for item in result:
                    for v in item.get("values", {}).get("values", []):
                        if v.get("value") is not None:
                            v["value"] = round(v["value"] / divisor, 2)
            return json.dumps({"result": result, "type": "labeled",
                               "metric": metric_name}, ensure_ascii=False)
    except Exception:
        pass

    # fallback: 非 labeled 指标（service_sla, service_resp_time, service_cpm 等）
    try:
        data = await gql("""query($dur:Duration!,$cond:MetricsCondition!){
            result:readMetricsValues(condition:$cond,duration:$dur){
            label values{values{value}}}}""",
            {"dur": dur, "cond": cond})
        result = data.get("result", {})
        if divisor != 1 and isinstance(result, dict):
            for v in result.get("values", {}).get("values", []):
                if v.get("value") is not None:
                    v["value"] = round(v["value"] / divisor, 2)
        return json.dumps({"result": result, "type": "regular",
                           "metric": metric_name}, ensure_ascii=False)
    except Exception:
        pass

    # fallback 2: 尝试 execExpression (10.x)
    entity = {"normal": True, "scope": scope, "serviceName": service_name}
    if endpoint_name:
        entity["endpointName"] = endpoint_name
    if instance_name:
        entity["serviceInstanceName"] = instance_name
    try:
        data = await gql("""query($expr:String!,$entity:Entity!,$dur:Duration!){
            result:execExpression(expression:$expr,entity:$entity,duration:$dur){
            type error results{metric{labels{key value}}
            values{id value traceID}}}}""",
            {"expr": expression, "entity": entity, "dur": dur})
        return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"All query methods failed for '{expression}'",
                           "detail": str(e)}, ensure_ascii=False)


@mcp.tool()
async def list_metrics(regex: str = "") -> str:
    """列出可用指标名称，可按正则过滤"""
    vars = {}
    if regex:
        vars["regex"] = regex
    data = await gql("""query($regex:String){
        listMetrics(regex:$regex){name type catalog}}""", vars)
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
async def query_logs(service_id: str = "", trace_id: str = "",
                     tags: str = "", start: str = "-30m",
                     end: str = "now", page_size: int = 20,
                     page_num: int = 1, order: str = "DES") -> str:
    """查询日志，支持按服务/traceId/标签过滤。tags格式: key=value,key2=value2"""
    dur = build_duration(start, end)
    cond: dict = {"queryDuration": dur,
                  "paging": {"pageNum": page_num, "pageSize": page_size,
                             "needTotal": True},
                  "queryOrder": order}
    if service_id:
        cond["serviceId"] = service_id
    if trace_id:
        cond["relatedTrace"] = {"traceId": trace_id}
    if tags:
        tag_list = []
        for pair in tags.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                tag_list.append({"key": k.strip(), "value": v.strip()})
        if tag_list:
            cond["tags"] = tag_list
    data = await gql("""query($cond:LogQueryCondition!){
        queryLogs(condition:$cond){logs{serviceName serviceInstanceName
        endpointName traceId timestamp contentType content tags{key value}}}}""",
        {"cond": cond})
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
async def query_alarms(keyword: str = "", start: str = "-1h",
                       end: str = "now", page_size: int = 20,
                       page_num: int = 1) -> str:
    """查询告警信息"""
    dur = build_duration(start, end)
    paging = {"pageNum": page_num, "pageSize": page_size, "needTotal": True}
    # SkyWalking 9.x getAlarm 参数结构
    data = await gql("""query($dur:Duration!,$paging:Pagination!,$kw:String){
        getAlarm(duration:$dur,paging:$paging,keyword:$kw){
        msgs{id message startTime scope
        tags{key value}}
        total}}""",
        {"dur": dur, "paging": paging, "kw": keyword or None})
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
async def query_services_topology(layer: str = "GENERAL",
                                  service_ids: str = "",
                                  start: str = "-30m",
                                  end: str = "now") -> str:
    """查询服务拓扑图。service_ids为逗号分隔的ID列表(可选)"""
    dur = build_duration(start, end)
    if service_ids:
        ids = [s.strip() for s in service_ids.split(",")]
        data = await gql("""query($ids:[ID!]!,$dur:Duration!){
            result:getServicesTopology(serviceIds:$ids,duration:$dur){
            nodes{id name type isReal} calls{id source target
            detectPoints sourceComponents targetComponents}}}""",
            {"ids": ids, "dur": dur})
    else:
        data = await gql("""query($layer:String!,$dur:Duration!){
            result:getGlobalTopology(layer:$layer,duration:$dur){
            nodes{id name type isReal} calls{id source target
            detectPoints sourceComponents targetComponents}}}""",
            {"layer": layer, "dur": dur})
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
async def query_events(service_id: str = "", start: str = "-1h",
                       end: str = "now", page_size: int = 20,
                       page_num: int = 1) -> str:
    """查询事件(部署/重启/扩缩容等)"""
    dur = build_duration(start, end)
    cond = {"time": dur,
            "paging": {"pageNum": page_num, "pageSize": page_size,
                       "needTotal": True},
            "order": "DES"}
    if service_id:
        cond["source"] = {"service": service_id}
    data = await gql("""query($cond:EventQueryCondition){
        queryEvents(condition:$cond){events{uuid source{service
        serviceInstance endpoint} name type message
        startTime endTime parameters{key value}}
        total}}""",
        {"cond": cond})
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
async def read_metrics_values(metric_name: str, service_name: str,
                              labels: str = "0,1,2,3,4",
                              start: str = "-30m", end: str = "now",
                              step: str = "MINUTE") -> str:
    """读取带标签的指标值(如service_percentile的P50/P75/P90/P95/P99)。
    对于非labeled指标(如service_sla/service_resp_time/service_cpm)也能自动处理。"""
    dur = build_duration(start, end, step)
    cond = {"name": metric_name,
            "entity": {"scope": "Service", "serviceName": service_name,
                       "normal": True}}

    # 先尝试 labeled 查询（适用于 service_percentile 等）
    label_list = [l.strip() for l in labels.split(",")]
    try:
        data = await gql("""query($dur:Duration!,$labels:[String!]!,$cond:MetricsCondition!){
            result:readLabeledMetricsValues(condition:$cond,labels:$labels,duration:$dur){
            label values{values{value}}}}""",
            {"dur": dur, "labels": label_list, "cond": cond})
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        pass

    # fallback: 使用 readMetricsValues（适用于 REGULAR_VALUE 类型指标）
    try:
        data = await gql("""query($dur:Duration!,$cond:MetricsCondition!){
            result:readMetricsValues(condition:$cond,duration:$dur){
            label values{values{value}}}}""",
            {"dur": dur, "cond": cond})
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        pass

    # fallback 2: 使用 readMetricsValue（单值查询，某些老版本）
    data = await gql("""query($dur:Duration!,$cond:MetricsCondition!){
        result:readMetricsValue(condition:$cond,duration:$dur)}""",
        {"dur": dur, "cond": cond})
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
async def query_endpoint_metrics(service_name: str,
                                 endpoint_name: str,
                                 metric_names: str = "endpoint_resp_time,endpoint_cpm,endpoint_sla",
                                 start: str = "-30m", end: str = "now",
                                 step: str = "MINUTE") -> str:
    """查询端点级别指标（响应时间、吞吐量、成功率等）。
    支持多个指标名逗号分隔。常用指标: endpoint_resp_time, endpoint_cpm, endpoint_sla, endpoint_percentile"""
    dur = build_duration(start, end, step)
    metrics = [m.strip() for m in metric_names.split(",")]
    results = {}

    for metric in metrics:
        cond = {"name": metric,
                "entity": {"scope": "Endpoint",
                           "serviceName": service_name,
                           "endpointName": endpoint_name,
                           "normal": True}}
        try:
            # 尝试 labeled 查询（如 endpoint_percentile）
            data = await gql("""query($dur:Duration!,$labels:[String!]!,$cond:MetricsCondition!){
                result:readLabeledMetricsValues(condition:$cond,labels:$labels,duration:$dur){
                label values{values{value}}}}""",
                {"dur": dur, "labels": ["0", "1", "2", "3", "4"], "cond": cond})
            results[metric] = data.get("result", [])
        except Exception:
            try:
                # fallback: 非 labeled 指标
                data = await gql("""query($dur:Duration!,$cond:MetricsCondition!){
                    result:readMetricsValues(condition:$cond,duration:$dur){
                    label values{values{value}}}}""",
                    {"dur": dur, "cond": cond})
                results[metric] = data.get("result", {})
            except Exception as e:
                results[metric] = {"error": str(e)}

    return json.dumps(results, ensure_ascii=False)


@mcp.tool()
async def query_slow_endpoints(service_id: str,
                               start: str = "-30m", end: str = "now",
                               limit: int = 20,
                               order: str = "DES") -> str:
    """查询服务的慢端点排序（Top-N 延迟最高的接口）"""
    dur = build_duration(start, end)
    # sortMetrics 查询 - SkyWalking 9.x 支持
    cond = {
        "name": "endpoint_resp_time",
        "parentService": service_id,
        "normal": True,
        "scope": "Endpoint",
        "topN": limit,
        "order": order
    }
    try:
        data = await gql("""query($cond:TopNCondition!,$dur:Duration!){
            result:sortMetrics(condition:$cond,duration:$dur){
            name id value refId}}""",
            {"cond": cond, "dur": dur})
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        pass

    # fallback: 尝试 getAllEndpointTopN (旧版本 API)
    try:
        data = await gql("""query($id:ID!,$dur:Duration!,$limit:Int!,$order:Order!){
            result:getAllEndpointTopN(serviceId:$id,duration:$dur,
            name:"endpoint_resp_time",topN:$limit,order:$order){
            name id value refId}}""",
            {"id": service_id, "dur": dur, "limit": limit, "order": order})
        return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
async def query_instance_metrics(service_name: str,
                                 instance_name: str,
                                 metric_names: str = "service_instance_resp_time,service_instance_cpm,service_instance_sla",
                                 start: str = "-30m", end: str = "now",
                                 step: str = "MINUTE") -> str:
    """查询实例级别指标。常用: service_instance_resp_time, service_instance_cpm, service_instance_sla,
    instance_jvm_cpu, instance_jvm_memory_heap, instance_jvm_young_gc_time, instance_jvm_old_gc_time"""
    dur = build_duration(start, end, step)
    metrics = [m.strip() for m in metric_names.split(",")]
    results = {}

    for metric in metrics:
        cond = {"name": metric,
                "entity": {"scope": "ServiceInstance",
                           "serviceName": service_name,
                           "serviceInstanceName": instance_name,
                           "normal": True}}
        try:
            data = await gql("""query($dur:Duration!,$cond:MetricsCondition!){
                result:readMetricsValues(condition:$cond,duration:$dur){
                label values{values{value}}}}""",
                {"dur": dur, "cond": cond})
            results[metric] = data.get("result", {})
        except Exception as e:
            results[metric] = {"error": str(e)}

    return json.dumps(results, ensure_ascii=False)


# ============ 启动入口 ============

if __name__ == "__main__":
    mcp.run()
