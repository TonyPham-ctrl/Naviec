sample_means <- replicate(K, {
    drawn <- lapply(strata, function(stratum) {
        stratum[sample(nrow(stratum), S, replace=FALSE), ]
    })
    # Mean of each sample k of each stratum.
    mu_h_hat <- sapply(drawn, function(d) mean(d$Mean))

    sum(weights * mu_h_hat)
})


sample_means <- replicate(K_hat, {
    drawn <- lapply(strata, function(stratum) {
        set.seed(seed)
        stratum[sample(nrow(stratum), s_d, replace=FALSE), ]
    })
    # Mean of each sample k of each stratum.
    variance <- sapply(drawn, function(d) var(d$Mean))
    # mu_h_hat <- sapply(drawn, function(d) mean(d$Mean))

    sum(weights * mu_h_hat)
})

SE_of_each_sample_of_a_stratum <- replicate(K_hat, {
    lapply(strata, function(stratum) {
        set.seed(seed)
        drawn <- stratum[sample(nrow(stratum), s_d, replace=FALSE), ]
        variance <- var(drawn$Mean)
        sqrt(`/`(1-`/`(s_d, nrow(stratum)), s_d)*variance)  #This is SE_hat_h_k
    })
})