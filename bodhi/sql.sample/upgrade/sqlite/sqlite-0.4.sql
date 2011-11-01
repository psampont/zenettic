ALTER TABLE bodhi_device ADD COLUMN "watt" integer default 140 not null;
ALTER TABLE bodhi_history ADD COLUMN "date" date;
update bodhi_history  set date = date(timestamp);
CREATE INDEX "bodhi_history_986cbc25" ON "bodhi_history" ("date");
