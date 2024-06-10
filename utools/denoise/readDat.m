function [data, dt, dx] = readDat(filename)
    fid = fopen(filename, 'r');
    D = fread(fid, 'float32');
    fclose(fid);

    fs = D(11);  % MATLAB索引从1开始
    dt = 1 / fs;
    dx = D(14);
    nx = int32(D(17));
    nt = int32(fs * D(18));
    
    % 从索引65开始重整形状，并转置，因为MATLAB默认使用列优先
    data = reshape(D(65:end), [nx, nt]).';
end
