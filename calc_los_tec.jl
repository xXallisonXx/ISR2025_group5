using HDF5, DataFrames, Measurements, Dates, CSV

function make_tec_df(filename)
    fid = h5open(filename, "r")

    beam_ids = read(fid["BeamCodes"])[1, :]
    timestamp = read(fid["Time/UnixTime"]) .|> unix2datetime
    # range = read(fid["FittedParams/Range"])
    # use altitude to calculate VTEC. Should just scale result by sin(elevation)
    alt = read(fid["FittedParams/Altitude"])
    Ne = read(fid["FittedParams/Ne"]) .± read(fid["FittedParams/dNe"])

    close(fid)

    cell_height = diff(alt, dims=1)
    # Bad solution to make cell_height the same shape as range
    # Shouldn't matter because all of the values in cell height should be the same (?)
    cell_height = [cell_height[1, :]'; cell_height]

    # Units m^2
    tec_per_cell = Ne .* cell_height

    # Replace NaN TEC with 0
    tec_per_cell[isnan.(tec_per_cell)] .= 0

    # TEC is calculated as a rectangular sum
    # This operation includes error propogation
    # The uncertainty in each Ne measurment is uncorrelated
    tec = sum(tec_per_cell, dims=1)

    # Remove range dimension since it is now length 1
    tec = tec[1, :, :]

    tec_value = Measurements.value.(tec)
    tec_uncert = Measurements.uncertainty.(tec)

    # Construct dataframe in tidy format
    df = vcat([DataFrame(
        beam_id=beam_ids[i],
        starttime=timestamp[1, :],
        TEC_per_m2=tec_value[i, :],
        dTEC_per_m2=tec_uncert[i, :]
    ) for i in eachindex(beam_ids)]...)

    return df

end

function collect_all_tec()
    files = readdir("data/sri", join=true)
    # Remove velocity files 
    ne_files = filter(f -> !occursin(r"vvels", f), files)

    df_per_file = [make_tec_df(file) for file in ne_files]

    for i in eachindex(ne_files)
        df_per_file[i].pulse_code .= match(r"\_(ac|lp)\_", ne_files[i]).captures[1]
        df_per_file[i].integration_time .= match(r"\_(\d+min)-", ne_files[i]).captures[1]
    end

    return vcat(df_per_file...)

end

collect_all_tec() |> CSV.write("data/pfisr_los_tec.csv")