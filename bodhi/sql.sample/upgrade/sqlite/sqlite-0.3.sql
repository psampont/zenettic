ALTER TABLE bodhi_device ADD COLUMN platform varchar(10) default 'win32' not null;
ALTER TABLE bodhi_history ADD COLUMN user varchar(20) default '' not null;
CREATE INDEX "bodhi_history_67f1b7ce" ON "bodhi_history" ("timestamp");
