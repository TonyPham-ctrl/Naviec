filepath <- paste('data/','partial_single_day.csv',sep="")

dat <- read.csv(filepath, sep=',', header=TRUE, dec='.', stringsAsFactors=TRUE)

# Initialise the stratum for each season, as seasonal change impact a lot on power usage
# The vector contains the months
morning_peak_hours <- c(7:8)
working_hours <- c(9:16)
evening_peak_hours <- c(17:18)
night_hours <- c(19:21)
sleep_hours <- c(22:23) 
sleep_hours <- append(sleep_hours, c(0:6))

library(lubridate)
library(dplyr)

dat$SETTLEMENTDATE <- format(as.POSIXct(dat$SETTLEMENTDATE, tz="", format("%Y-%m-%d %H:%M:%S")), format("%Y-%m-%d %H"))

dat <- dat %>% group_by(SETTLEMENTDATE) %>% dplyr::summarise(Mean=mean(RRP))

dat$hour <- as.integer(substr(dat$SETTLEMENTDATE, 12, 13))

dat$stratum <- case_when(
    dat$hour %in% morning_peak_hours ~ "morning_peak",
    dat$hour %in% working_hours      ~ "working",
    dat$hour %in% evening_peak_hours ~ "evening_peak",
    dat$hour %in% night_hours        ~ "night",
    dat$hour %in% sleep_hours        ~ "sleep",
    TRUE                             ~ NA_character_
)

dat$SETTLEMENTDATE <- NULL
dat$hour <- NULL
strata <- split(dat, dat$stratum)

length_of_stratum <- sapply(strata, function(stratum) nrow(stratum))
length_of_stratum
N <- sum(unlist(length_of_stratum, use.names=FALSE))
weights <- sapply(strata, function(stratum) nrow(stratum)/N)

# each_stratum_sample_size <- sapply(length_of_stratum, function(l) l-l+S )
# each_stratum_sample_size

# choose(703,1)*choose(1095,1)*choose(1095,1)*choose(3284,1)*choose(2555,1)
# choose(2555,2)

K <- 10000   
S <- 2       
sample_means <- replicate(K, {
    drawn <- lapply(strata, function(stratum) {
        stratum[sample(nrow(stratum), S), ]
    })
    mu_h_hat <- sapply(drawn, function(d) mean(d$Mean))
    sum(weights * mu_h_hat)
})
sample_means

help(replicate)
