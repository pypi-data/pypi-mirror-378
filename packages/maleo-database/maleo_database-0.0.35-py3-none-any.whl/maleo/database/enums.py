from enum import StrEnum


class CacheOrigin(StrEnum):
    CLIENT = "client"
    SERVICE = "service"


class CacheLayer(StrEnum):
    REPOSITORY = "repository"
    SERVICE = "service"
    CONTROLLER = "controller"
    MIDDLEWARE = "middleware"


class Connection(StrEnum):
    ASYNC = "async"
    SYNC = "sync"


class Driver(StrEnum):
    # SQL Databases - Most Popular
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"

    # SQL Databases - Enterprise
    MSSQL = "mssql"

    # NoSQL Document Stores
    MONGODB = "mongodb"

    # NoSQL Key-Value
    REDIS = "redis"

    # Search Engines
    ELASTICSEARCH = "elasticsearch"


class PostgreSQLSSLMode(StrEnum):
    DISABLE = "disable"
    ALLOW = "allow"
    PREFER = "prefer"
    REQUIRE = "require"
    VERIFY_CA = "verify-ca"
    VERIFY_FULL = "verify-full"


class MySQLCharset(StrEnum):
    UTF8 = "utf8"
    UTF8MB4 = "utf8mb4"
    LATIN1 = "latin1"
    ASCII = "ascii"


class MongoReadPreference(StrEnum):
    PRIMARY = "primary"
    PRIMARY_PREFERRED = "primaryPreferred"
    SECONDARY = "secondary"
    SECONDARY_PREFERRED = "secondaryPreferred"
    NEAREST = "nearest"


class ElasticsearchScheme(StrEnum):
    HTTP = "http"
    HTTPS = "https"


class PoolingStrategy(StrEnum):
    FIXED = "fixed"
    DYNAMIC = "dynamic"
    OVERFLOW = "overflow"
    QUEUE = "queue"
