ALTER TABLE bodhi_history ADD COLUMN date date;
update bodhi_history  set date = date(timestamp);
CREATE INDEX "bodhi_history_986cbc25" ON "bodhi_history" ("date");
CREATE INDEX "bodhi_history_67f1b7ce" ON "bodhi_history" ("timestamp");
