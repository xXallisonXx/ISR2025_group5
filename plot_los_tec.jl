using CSV, DataFrames, Plots, Dates
using Plots.PlotMeasures

fulldf = CSV.read("data/pfisr_los_tec.csv", DataFrame)

fulldf.TEC = fulldf.TEC_per_m2 * 1e-16
fulldf.dTEC = fulldf.dTEC_per_m2 * 1e-16

tticks = DateTime("2025-07-22T04:00:00.0"):Minute(30):DateTime("2025-07-22T06:00:00.0")
tticks_label = Dates.format.(tticks, "HH:MM")

beamcodes = ["64016", "64157", "64964", "65066"]
az = Dict("64016" => 14.04, "64157" => -154.3, "64964" => -34.69, "65066" => 75.03)
el = Dict("64016" => 90, "64157" => 77.5, "64964" => 66.09, "65066" => 65.56)

code_lut = Dict("lp" => "Long Pulse", "ac" => "Alternating Code")
it_lut = Dict(
    "1min" => "1 Minute",
    "3min" => "3 Minute",
    "5min" => "5 Minute",
    "10min" => "10 Minute",
    "15min" => "15 Minute",
    "20min" => "20 Minute"
)

tecdf = unstack(fulldf, [:starttime, :pulse_code, :integration_time], :beam_id, :TEC)
dtecdf = unstack(fulldf, [:starttime, :pulse_code, :integration_time], :beam_id, :dTEC)
widedf = innerjoin(tecdf, dtecdf, on=[:starttime, :pulse_code, :integration_time], renamecols="tec" => "dtec")
groupdf = groupby(widedf, [:pulse_code, :integration_time])

using Dates

for df in groupdf
    plot(
        [plot(
            df.starttime,
            df[!, "$bc.0tec"],
            yerr=df[!, "$bc.0dtec"],
            dpi=300,
            label=false,
            title="beamcode=$bc az=$(az[bc])° el=$(el[bc])°",
            xticks=(tticks, tticks_label),
            xlabel="Time on 2025-07-22 (UT)",
            ylabel="VTEC (TECU)",
            size=(960, 720),
            ylims=(0, 20)
        ) for bc in beamcodes]...,
        suptitle="$(code_lut[df.pulse_code[1]]) $(it_lut[df.integration_time[1]]) Integtration",
        left_margin=5mm, right_margin=5mm
    )
    savefig("figs/$(df.pulse_code[1])_$(df.integration_time[1]).png")
end