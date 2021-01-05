CREATE TABLE waermezaehler (
  datum            datetime NOT NULL DEFAULT 'current_timestamp()' COMMENT 'Das Datum wann der Eintrag erstellt wurde',
  zaehlerstand     int(10) UNSIGNED NOT NULL COMMENT 'Der Gesamtverbrauch der auf dem Zaehler abzulesen ist',
  durchlauf        float UNSIGNED NOT NULL COMMENT 'Der Gesamt Wasserdurchlauf der vom Heizkraftwerk kommt',
  betriebsstunden  int(10) UNSIGNED NOT NULL COMMENT 'Wieviele Stunden der Zahler schon ohne Reset online ist',
  fehlstunden      int(10) UNSIGNED NOT NULL COMMENT 'Wieviele Stunden der Zahler nicht zaehlen konnte. Hack',
  flowhours        int(10) UNSIGNED NOT NULL COMMENT 'Wieviele Stunden ein Wasserfluss gemessen wurde',
  /* Keys */
  PRIMARY KEY (datum)
) ENGINE = InnoDB;
