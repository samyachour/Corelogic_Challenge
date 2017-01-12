library(RPostgreSQL)

drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname = "parcels",
                 host = "localhost", port = 5432,
                 user = "samy")

dbExistsTable(con, "parcelterminal")