CREATE TABLE megamillions
  (
  epoch       INTEGER(17) DEFAULT '-',
  date        CHAR(10) DEFAULT '-',
  weekday     CHAR(10) DEFAULT '-',
  num1        INTEGER(2) DEFAULT '-',
  num2        INTEGER(2) DEFAULT '-',
  num3        INTEGER(2) DEFAULT '-',
  num4        INTEGER(2) DEFAULT '-',
  num5        INTEGER(2) DEFAULT '-',
  moneyball   INTEGER(2) DEFAULT '-',
  jackpot     DECIMAL(8) DEFAULT '-',
  lddate      INTEGER(17) DEFAULT -9999999999,
  PRIMARY KEY (epoch)
);

CREATE TABLE powerball
  (
  epoch       INTEGER(17) DEFAULT '-',
  date        CHAR(10) DEFAULT '-',
  weekday     CHAR(10) DEFAULT '-',
  num1        INTEGER(2) DEFAULT '-',
  num2        INTEGER(2) DEFAULT '-',
  num3        INTEGER(2) DEFAULT '-',
  num4        INTEGER(2) DEFAULT '-',
  num5        INTEGER(2) DEFAULT '-',
  moneyball   INTEGER(2) DEFAULT '-',
  jackpot     DECIMAL(8) DEFAULT '-',
  lddate      INTEGER(17) DEFAULT -9999999999,
  PRIMARY KEY (epoch)
);

