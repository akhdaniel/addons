CREATE TABLE   "SET_CHANGE_ACCOUNT"
(
  "P_CLIENT_TYPE" numeric(1,0),
  "P_CLIENT_ID" character varying(12),
  "P_SERVICE_ID" numeric(2,0),
  "P_OPERATION" numeric(1,0),
  "P_AMOUNT" numeric(14,2),
  "P_DATE_OPERATION" timestamp(0),
  "P_INVOICE" character varying(22),
  "P_DATE" timestamp(0),
  "P_DATE_EXCHANGE" timestamp(0),
  "P_GUID" character varying(40) NOT NULL
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "SET_CHANGE_ACCOUNT"
  OWNER TO postgres;

-- Index erpexchange.si_set_change_account_date

DROP INDEX IF EXISTS si_set_change_account_date;

CREATE INDEX si_set_change_account_date
  ON "SET_CHANGE_ACCOUNT"
  USING btree
  ("P_DATE_EXCHANGE", "P_DATE");

DROP INDEX IF EXISTS si_set_change_account_guid;

CREATE UNIQUE INDEX si_set_change_account_guid
  ON "SET_CHANGE_ACCOUNT"
  USING btree
  ("P_GUID");

---------------------------------------------------------------------------------------------------
-- Table erpexchange."SET_CLIENT_ACCOUNT"
-- Is used to store clients' accounts adding and deleting records
---------------------------------------------------------------------------------------------------

CREATE TABLE   "SET_CLIENT_ACCOUNT"
(
  "P_CLIENT_TYPE" numeric(1,0),
  "P_CLIENT_ID" character varying(12),
  "P_SERVICE_ID" numeric(2,0),
  "P_OPERATION" numeric(1,0),
  "P_NOTIFICATION_LIMIT" numeric(14,2),
  "P_ALERT_LIMIT" numeric(14,2),
  "P_DATE" timestamp(0),
  "P_DATE_EXCHANGE" timestamp(0),
  "P_GUID" character varying(40) NOT NULL
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "SET_CLIENT_ACCOUNT"
  OWNER TO postgres;

-- Index erpexchange.si_set_client_account_date

DROP INDEX IF EXISTS si_set_client_account_date;

CREATE INDEX si_set_client_account_date
  ON "SET_CLIENT_ACCOUNT"
  USING btree
  ("P_DATE_EXCHANGE", "P_DATE");

DROP INDEX IF EXISTS si_set_client_account_guid;

CREATE UNIQUE INDEX si_set_client_account_guid
  ON "SET_CLIENT_ACCOUNT"
  USING btree
  ("P_GUID");
---------------------------------------------------------------------------------------------------
-- Table erpexchange."SET_CLIENT_INFO"
-- Is used to store clients adding, editing and deleting records
---------------------------------------------------------------------------------------------------

CREATE TABLE   "SET_CLIENT_INFO"
(
  "P_CLIENT_TYPE" numeric(1,0),
  "P_CLIENT_ID" character varying(12),
  "P_CLIENT_NAME" character varying(40),
  "P_ADRES" character varying(255),
  "P_ADRES_FACT" character varying(255),
  "P_EMAIL" character varying(100),
  "P_NAME_FOR_REPORTS" character varying(255),
  "P_COMMENTS" character varying(100),
  "P_OPERATION" numeric(1,0),
  "P_CONTACT_PERSON" character varying(40),
  "P_DATE" timestamp(0),
  "P_DATE_EXCHANGE" timestamp(0),
  "P_GUID" character varying(40) NOT NULL
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "SET_CLIENT_INFO"
  OWNER TO postgres;

-- Index erpexchange.si_set_client_info_date

DROP INDEX IF EXISTS si_set_client_info_date;

CREATE INDEX si_set_client_info_date
  ON "SET_CLIENT_INFO"
  USING btree
  ("P_DATE_EXCHANGE", "P_DATE");

DROP INDEX IF EXISTS si_set_client_info_guid;

CREATE UNIQUE INDEX si_set_client_info_guid
  ON "SET_CLIENT_INFO"
  USING btree
  ("P_GUID");

---------------------------------------------------------------------------------------------------
-- Table erpexchange."TRANSACTIONS"
-- Is used to store clients adding, editing and deleting records
---------------------------------------------------------------------------------------------------

CREATE TABLE   "TRANSACTIONS"
(
  "P_DATETIME" numeric(14,0),
  "P_CLIENT_ID" character varying(12),
  "P_POS_NUMBER" numeric(4,0),
  "P_CLIENT_TYPE" numeric(1,0),
  "P_SERVICE_ID" numeric(4,0),
  "P_AMOUNT" numeric,
  "P_TERMINAL_PRICE" numeric,
  "P_TOTAL_AMOUNT" numeric,
  "P_ACTUAL_PRICE" numeric,
  "P_TOTAL_AMOUNT_WITHOUT_DISC" numeric,
  "P_GUID" character varying(32),
  "P_OPERATION_ID" numeric(1,0),
  "P_COMMENT" character varying(20),
  "P_DATE" timestamp(0),
  "P_DATE_EXCHANGE" timestamp(0)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "TRANSACTIONS"
  OWNER TO postgres;

-- Index erpexchange.si_transactions_date

DROP INDEX IF EXISTS si_transactions_date;

CREATE INDEX si_transactions_date
  ON "TRANSACTIONS"
  USING btree
  ("P_DATE_EXCHANGE", "P_DATE");

---------------------------------------------------------------------------------------------------
-- Table erpexchange."BONUSES"
-- LC bonus transactions
---------------------------------------------------------------------------------------------------

CREATE TABLE   "BONUSES"
(
  "P_DATETIME" numeric(14,0),
  "P_GUID" character varying(32),
  "P_CLIENT_ID" character varying(12),
  "P_CLIENT_TYPE" numeric,
  "P_OPERATION_ID" numeric, -- Operation type (ì1î, ì2î, ì3î, ì4î, ì5î)
  "P_COMMENT" character varying(23), -- Comment to ìOPERATION_IDî...
  "P_BONUS" numeric(14,2),
  "P_POS_ID" numeric(12,0),
  "P_POS_GROUP_ID" numeric(12,0),
  "P_DATE" timestamp(0),
  "P_DATE_EXCHANGE" timestamp(0)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE "BONUSES"
  OWNER TO postgres;
COMMENT ON COLUMN "BONUSES"."P_OPERATION_ID" IS 'Operation type (ì1î, ì2î, ì3î, ì4î, ì5î)';
COMMENT ON COLUMN "BONUSES"."P_COMMENT" IS 'Comment to ìOPERATION_IDî
1 ó ìBonus accumulationî;
2 ó ìBonus cancellationî;
3 ó ìManual bonus removalî;
4 ó ìAutomatic bonus removalî;
5 ó ìBonus change in OCî.';

