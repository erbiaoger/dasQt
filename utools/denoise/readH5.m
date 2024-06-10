function [data, dx, dt, nt, nx] = readH5(filename)
    info = h5info(filename);
    for k = 1:length(info.Groups)
        group_name = info.Groups(k).Name;
        strainRatePath = strcat(group_name, '/Source1/Zone1/StrainRate');
        spacingAttrPath = strcat(group_name, '/Source1/Zone1');
        
        StrainRate = h5read(filename, strainRatePath);
        spacing = h5readatt(filename, spacingAttrPath, 'Spacing');
    end

    dx = spacing(1);
    dt = spacing(2) * 1e-3;
    [nb, nt, nx] = size(StrainRate);
    data = reshape(StrainRate(:, floor(nt/2)+1:end, :), [], nx);
    [nt, nx] = size(data);

    return
end
