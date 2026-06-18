"""
SkyWalking MCP Server - Python 实现
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
    cond = {"queryDuration": dur, "traceState": trace_state,
            "paging": {"pageNum": page_num, "pageSize": page_size},
            "queryOrder": order}
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
    data = await gql("""query($cond:TraceQueryCondition){
        result:queryTraces(condition:$cond){traces{spans{
        traceId segmentId spanId parentSpanId serviceCode serviceInstanceName
        startTime endTime endpointName type peer component isError layer
        tags{key value} logs{time data{key value}}
        refs{traceId parentSegmentId parentSpanId type}}}}}""",
        {"cond": cond})
    return json.dumps(data, ensure_ascii=False)


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
    """执行MQE指标表达式查询(如service_cpm,service_resp_time,service_percentile等)"""
    dur = build_duration(start, end, step)
    entity = {}
    if service_name:
        entity["serviceName"] = service_name
        entity["normal"] = True
    if endpoint_name:
        entity["endpointName"] = endpoint_name
    if instance_name:
        entity["serviceInstanceName"] = instance_name
    data = await gql("""query($expr:String!,$entity:Entity!,$dur:Duration!){
        execExpression(expression:$expr,entity:$entity,duration:$dur){
        type error results{metric{labels{key value}}
        values{id value traceID}}}}""",
        {"expr": expression, "entity": entity, "dur": dur})
    return json.dumps(data, ensure_ascii=False)


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
                  "paging": {"pageNum": page_num, "pageSize": page_size},
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
    data = await gql("""query($cond:LogQueryCondition){
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
    data = await gql("""query($dur:Duration!,$paging:Pagination!,$kw:String){
        getAlarm(duration:$dur,paging:$paging,keyword:$kw){
        msgs{id message startTime scope
        scope{service serviceInstance endpoint}
        tags{key value}}}}""",
        {"dur": dur, "paging": {"pageNum": page_num, "pageSize": page_size},
         "kw": keyword or None})
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
            "paging": {"pageNum": page_num, "pageSize": page_size},
            "order": "DES"}
    if service_id:
        cond["source"] = {"service": service_id}
    data = await gql("""query($cond:EventQueryCondition){
        queryEvents(condition:$cond){events{uuid source{service
        serviceInstance endpoint} name type message
        startTime endTime parameters{key value}}}}""",
        {"cond": cond})
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
async def read_metrics_values(metric_name: str, service_name: str,
                              labels: str = "0,1,2,3,4",
                              start: str = "-30m", end: str = "now",
                              step: str = "MINUTE") -> str:
    """读取带标签的指标值(如service_percentile的P50/P75/P90/P95/P99)"""
    dur = build_duration(start, end, step)
    label_list = [l.strip() for l in labels.split(",")]
    cond = {"name": metric_name,
            "entity": {"scope": "Service", "serviceName": service_name,
                       "normal": True}}
    data = await gql("""query($dur:Duration!,$labels:[String!]!,$cond:MetricsCondition!){
        result:readLabeledMetricsValues(condition:$cond,labels:$labels,duration:$dur){
        label values{values{value}}}}""",
        {"dur": dur, "labels": label_list, "cond": cond})
    return json.dumps(data, ensure_ascii=False)


# ============ 启动入口 ============

if __name__ == "__main__":
    mcp.run()
