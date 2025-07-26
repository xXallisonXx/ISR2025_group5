using HDF5, DataFrames, Dates, Plots

pf_lat = 65.1992
pf_lon = -147.47104

# Read in GNSS Data

gnss_fid = h5open("data/ipy27_vs_gnss/gps250701g.001.hdf5", "r")

gnss_df = read(gnss_fid["Data/Table Layout"]) |> DataFrame

gnss_df = gnss_df[gnss_df.gdlat.==65 .&& gnss_df.glon.==-147, [:ut1_unix, :tec, :dtec]]
gnss_df.timestamp = unix2datetime.(gnss_df.ut1_unix)

close(gnss_fid)

# Read in Long Pulse PFISR Data

lp_fid = h5open("data/ipy27_vs_gnss/pfa20250701.001_lp_fit_05min.001.h5", "r")

lp_df = read(lp_fid["Data/Table Layout"]) |> DataFrame

lp_df = lp_df[lp_df.elm.==90 .&& lp_df.range .≥ 200e3, [:ut1_unix, :ne, :dne]]

lp_df.cell_height .= 6000

close(lp_fid)

# Read in Alternating Code PFISR Data

ac_fid = h5open("data/ipy27_vs_gnss/pfa20250701.001_ac_fit_05min.001.h5", "r")

ac_df = read(ac_fid["Data/Table Layout"]) |> DataFrame

ac_df = ac_df[ac_df.elm.==90 .&& ac_df.range .< 200e3, [:ut1_unix, :ne, :dne, :range]]

ac_df.cell_height .= 4500
ac_df[ac_df.range .> 1.15e5, :cell_height] .= 5246
ac_df[ac_df.range .> 1.25e5, :cell_height] .= 8994
ac_df[ac_df.range .> 1.5e5, :cell_height] .= 17988

ac_df = ac_df[:, [:ut1_unix, :ne, :dne, :cell_height]]

close(ac_fid)

# Calculate TEC from PFISR Data

ne_df = vcat(lp_df, ac_df)
ne_df.cell_tec = ne_df.ne .* ne_df.cell_height * 1e-16
ne_df.cell_dtec = ne_df.dne .* ne_df.cell_height * 1e-16

ne_df.timestamp = unix2datetime.(ne_df.ut1_unix)

ne_df = ne_df[ne_df.timestamp .≤ DateTime("2025-07-02T00:00:00"), :]
ne_df = ne_df[.!isnan.(ne_df.ne) .&& .!isnan.(ne_df.dne), :]

ne_time_groups = groupby(ne_df, :timestamp)

tec = combine(ne_time_groups, :cell_tec => sum => :tec)
dtec = combine(ne_time_groups, :cell_tec => (u -> sqrt(sum(u .^ 2))) => :dtec)

tec_df = innerjoin(tec, dtec, on=:timestamp)

# Plot Comparison

starttime = DateTime("2025-07-01T00:00:00.0")
endtime = DateTime("2025-07-02T00:00:00.0")

tticks = starttime:Hour(2):endtime
tticks_label = Dates.format.(tticks, "HH:MM")

plot(
    gnss_df.timestamp, 
    gnss_df.tec, 
    label="GNSS",
    c=1, 
    xlims=Dates.value.([starttime, endtime]),
    xticks = (tticks, tticks_label),
    dpi=300
)

plot!(
    gnss_df.timestamp, 
    gnss_df.tec .- gnss_df.dtec,
    fillrange=gnss_df.tec .+ gnss_df.dtec,
    alpha=0.35,
    c=1, 
    label=false
)

plot!(
    tec_df.timestamp, 
    tec_df.tec, 
    label="PFISR",
    c=2
)

plot!(
    tec_df.timestamp, 
    tec_df.tec .- tec_df.dtec,
    fillrange=tec_df.tec .+ tec_df.dtec,
    alpha=0.35,
    c=2, 
    label=false
)

xlabel!("Time on 2025-07-01 (UT)")
ylabel!("VTEC (TECU)")

savefig("figs/july_1_comparison.png")