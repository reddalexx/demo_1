#!/usr/bin/env sh

CLICKHOUSE_DB="${CLICKHOUSE_DB:-database}";
CLICKHOUSE_USER="${CLICKHOUSE_USER:-user}";
CLICKHOUSE_PASSWORD="${CLICKHOUSE_PASSWORD:-password}";

cat <<EOT >> /etc/clickhouse-server/users.d/user.xml
<yandex>
  <!-- Docs: <https://clickhouse.tech/docs/en/operations/settings/settings_users/> -->
  <users>
    <${CLICKHOUSE_USER}>
      <profile>default</profile>
      <networks>
        <ip>::/0</ip>
      </networks>
      <password>${CLICKHOUSE_PASSWORD}</password>
      <quota>default</quota>
    </${CLICKHOUSE_USER}>
  </users>
</yandex>
EOT
#cat /etc/clickhouse-server/users.d/user.xml;

clickhouse-client --user "${CLICKHOUSE_USER}" --password "${CLICKHOUSE_PASSWORD}" --query "CREATE DATABASE IF NOT EXISTS ${CLICKHOUSE_DB}";

QUERY=${DOLLAR}(cat << EOM
CREATE TABLE IF NOT EXISTS ${CLICKHOUSE_DB}.${CLICKHOUSE_NGINX_TABLE} (
    RemoteAddr String,
    RemoteUser String,
    TimeLocal DateTime,
    Date Date DEFAULT toDate(TimeLocal),
    Request String,
    RequestMethod String,
    Status Int32,
    BytesSent Int64,
    HttpReferer String,
    HttpUserAgent String,
    RequestTime Float32,
    UpstreamConnectTime Float32,
    UpstreamHeaderTime Float32,
    UpstreamResponseTime Float32,
    Https FixedString(2),
    ConnectionsWaiting Int64,
    ConnectionsActive Int64
) ENGINE = MergeTree(Date, (Status, Date), 8192)
EOM
)

clickhouse-client --user "${CLICKHOUSE_USER}" --password "${CLICKHOUSE_PASSWORD}" --query "${DOLLAR}QUERY"