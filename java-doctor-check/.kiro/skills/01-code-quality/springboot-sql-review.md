---
inclusion: fileMatch
fileMatchPattern: "**/*.xml,**/*Mapper.java,**/*Repository.java,**/*Dao.java"
---

# Spring Boot 项目 SQL 安全与性能审查 Skill

当打开 MyBatis XML、Mapper 接口、Repository、DAO 文件时自动加载。
审查 Spring Boot 项目中 Java 代码与 SQL 的交互，结合项目中的建表脚本和索引定义进行综合分析。

---

## 审查前准备（重要）

审查当前文件时，请主动搜索项目中的相关文件以获取完整上下文：

1. **建表脚本**：搜索 `**/*.sql` 文件中的 CREATE TABLE 语句，获取表结构和索引定义
2. **MyBatis XML**：搜索 `**/mapper/**/*.xml` 或 `**/mybatis/**/*.xml`
3. **实体类**：搜索对应的 Entity/PO/DO 类，了解字段映射
4. **配置文件**：搜索 `application*.yml` 或 `application*.properties` 中的数据源配置
5. **其他 Mapper/DAO**：搜索相关表的其他查询，了解查询模式

结合以上信息，对比 SQL 查询与实际表结构/索引，给出精准的优化建议。

---

## 一、MyBatis 审查

### 1.1 SQL 注入防护（最高优先级）

**${} vs #{} 使用审查**
```xml
<!-- ❌ 严重：${} 直接拼接，SQL 注入风险 -->
<select id="findByName" resultType="User">
  SELECT * FROM t_user WHERE name = '${name}'
</select>

<!-- ✅ 正确：#{} 参数化查询 -->
<select id="findByName" resultType="User">
  SELECT * FROM t_user WHERE name = #{name}
</select>

<!-- ⚠️ 必须使用 ${} 的场景，需要严格白名单校验 -->
<!-- 场景1：动态表名 -->
<select id="findByTable" resultType="Map">
  SELECT * FROM ${tableName} WHERE id = #{id}
  <!-- tableName 必须在 Java 层做白名单校验 -->
</select>

<!-- 场景2：动态排序字段 -->
<select id="findWithOrder" resultType="User">
  SELECT * FROM t_user ORDER BY ${orderColumn} ${orderDirection}
  <!-- orderColumn 和 orderDirection 必须白名单校验 -->
</select>

<!-- 场景3：动态 IN 列表 — 不需要用 ${} -->
<!-- ❌ 错误做法 -->
<select id="findByIds">
  SELECT * FROM t_user WHERE id IN (${ids})
</select>
<!-- ✅ 正确做法：使用 foreach -->
<select id="findByIds" resultType="User">
  SELECT * FROM t_user WHERE id IN
  <foreach collection="ids" item="id" open="(" separator="," close=")">
    #{id}
  </foreach>
</select>
```

**检查所有 ${} 使用**
- 搜索项目中所有 MyBatis XML 文件中的 `${}` 使用
- 每个 `${}` 都必须确认：是否有白名单校验？是否可以改为 `#{}`？
- 特别关注：用户输入直接传入 `${}` 的场景

### 1.2 动态 SQL 审查

**if/where/choose 标签**
```xml
<!-- ⚠️ 检查动态条件是否可能导致全表扫描 -->
<select id="findOrders" resultType="Order">
  SELECT order_id, user_id, amount, status
  FROM t_order
  <where>
    <if test="userId != null">
      AND user_id = #{userId}
    </if>
    <if test="status != null">
      AND status = #{status}
    </if>
    <if test="startTime != null">
      AND create_time >= #{startTime}
    </if>
  </where>
  <!-- ❌ 风险：如果所有条件都为 null，变成全表查询 -->
  <!-- ✅ 建议：至少有一个必填条件，或加 LIMIT 兜底 -->
  LIMIT #{pageSize}
</select>

<!-- ⚠️ 检查 LIKE 查询 -->
<if test="keyword != null and keyword != ''">
  <!-- ❌ 左模糊，索引失效 -->
  AND name LIKE CONCAT('%', #{keyword}, '%')
  <!-- ✅ 右模糊，可以使用索引 -->
  AND name LIKE CONCAT(#{keyword}, '%')
  <!-- 如果必须全模糊，建议使用 Elasticsearch -->
</if>
```

**foreach 标签**
```xml
<!-- ⚠️ 检查 IN 列表大小 -->
<select id="findByIds" resultType="User">
  SELECT * FROM t_user WHERE id IN
  <foreach collection="ids" item="id" open="(" separator="," close=")">
    #{id}
  </foreach>
  <!-- ❌ 风险：ids 列表过大（>1000）会导致性能问题 -->
  <!-- ✅ 建议：Java 层限制列表大小，超过时分批查询 -->
</select>

<!-- 批量插入 -->
<insert id="batchInsert">
  INSERT INTO t_order (user_id, amount, status)
  VALUES
  <foreach collection="list" item="item" separator=",">
    (#{item.userId}, #{item.amount}, #{item.status})
  </foreach>
  <!-- ⚠️ 检查批量大小，单次不超过 1000 条 -->
  <!-- MySQL 有 max_allowed_packet 限制 -->
</insert>
```

### 1.3 ResultMap 与映射审查

```xml
<!-- ⚠️ 检查 N+1 查询问题 -->
<!-- ❌ 嵌套查询（每行触发一次子查询） -->
<resultMap id="orderWithUser" type="Order">
  <association property="user" column="user_id"
    select="com.example.mapper.UserMapper.findById"/>
  <!-- 查询 100 个订单会触发 100 次 UserMapper.findById -->
</resultMap>

<!-- ✅ 嵌套结果（一次 JOIN 查询） -->
<resultMap id="orderWithUser" type="Order">
  <association property="user" javaType="User">
    <result property="id" column="user_id"/>
    <result property="name" column="user_name"/>
  </association>
</resultMap>
<select id="findOrdersWithUser" resultMap="orderWithUser">
  SELECT o.*, u.name AS user_name
  FROM t_order o LEFT JOIN t_user u ON o.user_id = u.id
  WHERE o.status = #{status}
</select>

<!-- 或使用 fetchType="lazy" 延迟加载 -->
<association property="user" column="user_id"
  select="com.example.mapper.UserMapper.findById"
  fetchType="lazy"/>
```

### 1.4 分页查询审查

```xml
<!-- ❌ 手动 LIMIT OFFSET 深分页 -->
<select id="findOrders" resultType="Order">
  SELECT * FROM t_order
  WHERE user_id = #{userId}
  ORDER BY create_time DESC
  LIMIT #{offset}, #{pageSize}
  <!-- offset 很大时性能极差 -->
</select>

<!-- ✅ 游标分页（推荐） -->
<select id="findOrders" resultType="Order">
  SELECT * FROM t_order
  WHERE user_id = #{userId}
  <if test="lastId != null">
    AND id &lt; #{lastId}
  </if>
  ORDER BY id DESC
  LIMIT #{pageSize}
</select>

<!-- ✅ 使用 PageHelper 插件时也要注意 -->
<!-- PageHelper 底层仍然是 LIMIT OFFSET，大页码时性能差 -->
<!-- 建议：限制最大页码，或提供游标分页 API -->
```


---

## 二、JPA/Hibernate 审查

### 2.1 查询性能

**N+1 问题检查**
```java
// ❌ 默认 LAZY 加载导致 N+1
@Entity
public class Order {
    @ManyToOne(fetch = FetchType.LAZY)
    private User user;
}
// 查询 100 个 Order 后遍历访问 user，触发 100 次额外查询

// ✅ 使用 @EntityGraph 或 JOIN FETCH
@EntityGraph(attributePaths = {"user"})
List<Order> findByStatus(Integer status);

// ✅ 或 JPQL JOIN FETCH
@Query("SELECT o FROM Order o JOIN FETCH o.user WHERE o.status = :status")
List<Order> findByStatusWithUser(@Param("status") Integer status);
```

**自动生成 SQL 审查**
```java
// ⚠️ JPA 方法名查询可能生成低效 SQL
// 检查生成的 SQL 是否有合适的索引

// 简单查询 — 通常没问题
List<Order> findByUserId(Long userId);
// 生成：SELECT * FROM t_order WHERE user_id = ?
// 检查：user_id 是否有索引？

// ⚠️ 复杂查询 — 可能生成低效 SQL
List<Order> findByUserIdAndStatusAndCreateTimeBetweenOrderByAmountDesc(
    Long userId, Integer status, LocalDateTime start, LocalDateTime end);
// 生成的 SQL 可能不走最优索引
// 建议：复杂查询用 @Query 手写 SQL，明确控制

// ❌ 避免使用 findAll() 无条件查询
List<Order> findAll();  // 全表扫描
```

**批量操作**
```java
// ❌ JPA 默认逐条 INSERT
for (Order order : orders) {
    orderRepository.save(order);  // 每次一条 INSERT
}

// ✅ 批量保存 + 配置批量大小
// application.yml:
// spring.jpa.properties.hibernate.jdbc.batch_size: 500
// spring.jpa.properties.hibernate.order_inserts: true
// spring.jpa.properties.hibernate.order_updates: true
orderRepository.saveAll(orders);

// ✅ 大批量用 JDBC 批量插入
@Modifying
@Query(value = "INSERT INTO t_order (user_id, amount) VALUES (:userId, :amount)",
       nativeQuery = true)
void batchInsert(@Param("userId") Long userId, @Param("amount") BigDecimal amount);
```

### 2.2 事务审查

```java
// ⚠️ @Transactional 常见问题

// ❌ 同类内部调用，事务不生效（代理失效）
@Service
public class OrderService {
    public void createOrder(Order order) {
        this.processOrder(order);  // ❌ 内部调用，@Transactional 不生效
    }

    @Transactional
    public void processOrder(Order order) {
        // 事务不会开启
    }
}

// ❌ 非 public 方法，事务不生效
@Transactional
private void processOrder(Order order) { }  // private 方法事务无效

// ❌ 默认只回滚 RuntimeException
@Transactional  // 默认 rollbackFor = RuntimeException.class
public void transfer() throws Exception {
    // 抛出 checked Exception 不会回滚
}
// ✅ 显式指定
@Transactional(rollbackFor = Exception.class)

// ❌ 大事务（事务中包含耗时操作）
@Transactional
public void processOrder(Order order) {
    orderMapper.insert(order);
    httpClient.callPayment(order);  // ❌ HTTP 调用不应在事务中
    accountMapper.deduct(order.getAmount());
}
// ✅ 拆分：耗时操作放在事务外
public void processOrder(Order order) {
    PaymentResult result = httpClient.callPayment(order);  // 事务外
    doInTransaction(order, result);  // 事务内只做 DB 操作
}

// ⚠️ 事务传播行为检查
@Transactional(propagation = Propagation.REQUIRES_NEW)
// REQUIRES_NEW 会挂起外层事务，开启新事务
// 注意：新事务独立提交/回滚，外层事务回滚不影响内层已提交的数据
```

---

## 三、JDBC / JdbcTemplate 审查

```java
// ❌ 字符串拼接 SQL（SQL 注入）
String sql = "SELECT * FROM t_user WHERE name = '" + name + "'";
jdbcTemplate.queryForList(sql);

// ✅ 参数化查询
String sql = "SELECT * FROM t_user WHERE name = ?";
jdbcTemplate.queryForList(sql, name);

// ❌ 未关闭资源
Connection conn = dataSource.getConnection();
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery(sql);
// 如果中间抛异常，资源泄漏

// ✅ try-with-resources
try (Connection conn = dataSource.getConnection();
     PreparedStatement stmt = conn.prepareStatement(sql)) {
    stmt.setString(1, name);
    try (ResultSet rs = stmt.executeQuery()) {
        // 处理结果
    }
}

// 批量操作
// ❌ 循环单条执行
for (Order order : orders) {
    jdbcTemplate.update("INSERT INTO t_order ...", order.getUserId(), order.getAmount());
}
// ✅ 批量执行
jdbcTemplate.batchUpdate("INSERT INTO t_order (user_id, amount) VALUES (?, ?)",
    new BatchPreparedStatementSetter() {
        public void setValues(PreparedStatement ps, int i) throws SQLException {
            ps.setLong(1, orders.get(i).getUserId());
            ps.setBigDecimal(2, orders.get(i).getAmount());
        }
        public int getBatchSize() { return orders.size(); }
    });
```

---

## 四、数据源与连接池审查

### 4.1 连接池配置检查

```yaml
# HikariCP 推荐配置（Spring Boot 默认连接池）
spring:
  datasource:
    hikari:
      # ⚠️ 检查以下配置是否合理
      maximum-pool-size: 20        # 最大连接数（CPU核数 × 2 + 磁盘数）
      minimum-idle: 10             # 最小空闲连接（建议等于 maximum-pool-size）
      connection-timeout: 3000     # 获取连接超时（3秒，不要太长）
      idle-timeout: 600000         # 空闲连接超时（10分钟）
      max-lifetime: 1800000        # 连接最大生命周期（30分钟，要小于 MySQL wait_timeout）
      leak-detection-threshold: 60000  # 连接泄漏检测（60秒，开发环境开启）

# ❌ 常见错误配置
      maximum-pool-size: 200       # 过大，数据库连接数有限
      connection-timeout: 30000    # 过长，请求会长时间等待
      minimum-idle: 1              # 过小，突发流量时需要频繁创建连接
```

### 4.2 多数据源审查

```java
// 多数据源场景检查：
// 1. 读写分离是否正确路由（写操作走主库，读操作走从库）
// 2. 事务中的查询是否走主库（避免主从延迟导致数据不一致）
// 3. 数据源切换是否在事务开始前（事务中切换数据源无效）

// ⚠️ 常见问题：@Transactional 中读操作走了从库
@Transactional
public void transfer(Long fromId, Long toId, BigDecimal amount) {
    Account from = accountMapper.findById(fromId);  // 应该走主库
    // 如果走从库，可能读到旧数据
}
```

---

## 五、索引与查询计划交叉审查

### 5.1 结合项目 SQL 脚本审查

审查 Java 代码中的 SQL 时，请执行以下交叉检查：

**步骤 1：提取查询中涉及的表**
- 从 MyBatis XML / JPA @Query / JdbcTemplate 中提取所有表名

**步骤 2：查找项目中的建表语句**
- 搜索项目中 `*.sql` 文件，找到对应表的 CREATE TABLE 语句
- 提取已有索引列表

**步骤 3：对比分析**
```
对于每个查询，检查：
1. WHERE 条件字段是否有索引？
2. JOIN 关联字段是否有索引？
3. ORDER BY 字段是否有索引？
4. GROUP BY 字段是否有索引？
5. 是否可以使用覆盖索引（查询字段全在索引中）？
6. 联合索引的字段顺序是否与查询匹配（最左前缀）？
7. 是否存在索引失效的写法（函数/表达式/隐式转换）？
```

**步骤 4：生成索引建议**
```
如果发现缺少索引，给出具体的 CREATE INDEX 语句：
  ALTER TABLE t_order ADD INDEX idx_user_status(user_id, status);

如果发现冗余索引，建议删除：
  已有索引 idx_user(user_id) 和 idx_user_status(user_id, status)
  → idx_user 是冗余的（被 idx_user_status 覆盖），建议删除

如果发现索引失效的写法，给出修改建议。
```

### 5.2 慢查询风险评估

对每个查询进行慢查询风险评估：

```
评估维度：
1. 是否全表扫描（无索引或索引失效）
2. 是否有大表 JOIN（两张大表关联）
3. 是否有深分页（OFFSET 很大）
4. 是否有子查询（相关子查询性能差）
5. 是否有 filesort（ORDER BY 未走索引）
6. 是否有临时表（GROUP BY 未走索引）
7. IN 列表是否可能过大
8. 动态 SQL 是否可能退化为全表查询

风险等级：
  🔴 高风险：预计 > 1s（全表扫描/大表无索引 JOIN/深分页）
  🟡 中风险：预计 100ms-1s（部分索引失效/filesort）
  🔵 低风险：预计 < 100ms（索引覆盖良好）
```

---

## 六、Spring Boot 特有检查项

### 6.1 SQL 日志配置
```yaml
# 开发环境应开启 SQL 日志
# MyBatis
mybatis:
  configuration:
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl

# JPA
spring:
  jpa:
    show-sql: true
    properties:
      hibernate:
        format_sql: true

# ⚠️ 生产环境必须关闭 SQL 日志（性能影响 + 敏感数据泄露）
```

### 6.2 MyBatis 配置检查
```yaml
mybatis:
  configuration:
    # ⚠️ 检查以下配置
    map-underscore-to-camel-case: true    # 下划线转驼峰（推荐开启）
    default-fetch-size: 100               # 默认 fetchSize（大结果集优化）
    default-statement-timeout: 30         # SQL 超时时间（秒）
    cache-enabled: false                  # 二级缓存（分布式环境建议关闭）
    lazy-loading-enabled: true            # 延迟加载
    aggressive-lazy-loading: false        # 按需加载（不要激进加载）
```

### 6.3 数据库安全配置
```yaml
# ⚠️ 检查数据库连接安全
spring:
  datasource:
    url: jdbc:mysql://host:3306/db?useSSL=true&requireSSL=true  # 开启 SSL
    # ❌ 密码不要明文写在配置文件中
    # password: 123456
    # ✅ 使用环境变量或配置中心
    # password: ${DB_PASSWORD}
```

---

## 七、审查输出格式

```
【问题类型】SQL注入 / 查询性能 / 索引缺失 / N+1问题 / 事务问题 / 连接池 / 配置安全
【严重程度】🔴 严重（SQL注入/全表扫描/事务失效/连接泄漏）
           🟡 警告（缺少索引/N+1/深分页/大事务）
           🔵 建议（SELECT */命名不规范/配置优化）
【问题位置】文件:行号 / Mapper方法名 / SQL片段
【问题描述】具体问题
【关联表结构】涉及的表和当前索引情况
【性能影响】预估查询耗时和影响范围
【修复建议】
  - Java 代码修改建议
  - SQL 修改建议
  - 索引修改建议（具体 DDL）
  - 配置修改建议
```

审查完成后给出：
1. SQL 安全评分（1-10）
2. 查询性能评分（1-10）
3. 索引覆盖分析报告（哪些查询缺索引）
4. 建议新增的索引列表（具体 DDL）
5. 建议删除的冗余索引
6. Top 3 优先修复项
