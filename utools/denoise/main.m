% 定义文件路径
folderPath = '/run/user/1000/gvfs/smb-share:server=ds920.local,share=csim_lab/DATA/Car-JLU-2024-01-31/ovlink/2024-02-01';
% 构造搜索路径
searchPattern = fullfile(folderPath, '*.dat');
% 获取路径下所有 .dat 文件
files = dir(searchPattern);
filename = files(130).name

[data, dt, dx] = readDat(fullfile(folderPath, filename));
data = data(:, 73:end);
disp('read done')

%% bandpass
[n1,n2]=size(data);
[nt, nx] = size(data);
t=[0:nt]*dt;
x=1:nx;

d_bp = bp_filter(data, dt, 0.01, 0.05, 1.9, 2.0);

h2 = figure(2)
imagesc(x,t,d_bp);
colormap(jet);
caxis([-0.001,0.001])
xlabel('Channel');
ylabel('Time (s)');
title('Band Pass')
saveas(h2,'bp.png');


% FK 
d_fk2=d_bp'-fk_dip(d_bp',0.0001);%0.0001
h4 = figure(4)
imagesc(x,t,d_fk2');
colormap(jet);
caxis([-0.001,0.001])
xlabel('Channel');
ylabel('Time (s)');
title('FK Filter')
saveas(h4,'fk.png');

%% Denoising using Curvelet method
tic
d_fk3=d_fk2;
[n1,n2]=size(d_fk3);
%%[n1,n2]=size(data);
is_real=1;           % Type of the transform(0: complex-valued curvelets,1: real-valued curvelets)
finest=1;            % Chooses one of two possibilities for the coefficients at the finest level(1: curvelets,2: wavelets)
alpha=0.03;           % Tresholding parameter  0.03
niter=10;

F=ones(n1,n2);                                  % 
X=fftshift(ifft2(F))*sqrt(prod(size(F)));  

C=fdct_wrapping(X,0,finest);                    % 
% Compute norm of curvelets (exact)
E=cell(size(C));
for s=1:length(C)
    E{s}=cell(size(C{s}));
    for w=1:length(C{s})
         A=C{s}{w};
         E{s}{w}=sqrt(sum(sum(A.*conj(A)))/prod(size(A)));    
    end
end

Cdn=fdct_wrapping(data,is_real,finest);

Smax=length(Cdn);
Sigma0=alpha*median(median(abs(Cdn{Smax}{1})))/0.58;     %0.58
Sigma=Sigma0;
sigma=[Sigma,linspace(2.5*Sigma,0.5*Sigma,niter)];
Sigma=sigma(1);

Cdn=fdct_wrapping(d_fk3,is_real,finest);
    Ct=Cdn;
    for s=2:length(Cdn)
        thresh=Sigma+Sigma*s;
        for w=1:length(Cdn{s})
            Ct{s}{w}=Cdn{s}{w}.*(abs(Cdn{s}{w})>thresh*E{s}{w});
        end
    end

d_curvelet=real(ifdct_wrapping(Ct,is_real,n1,n2));
toc

h5 = figure(5)
imagesc(x,t,d_curvelet');
colormap(jet);
caxis([-0.001,0.001])
xlabel('Channel');
ylabel('Time (s)');
title('d_curvelet')
saveas(h5,'d_curvelet.png');



h6 = figure(6)
imagesc(x, t, d_fk2'-d_bp)
colormap(jet);
caxis([-0.001,0.001])
xlabel('Channel');
ylabel('Time (s)');
title('fk - bp')
saveas(h6,'fk_bp.png');


h7 = figure(7)
imagesc(x, t, d_curvelet'-d_fk2')
colormap(jet);
caxis([-0.001,0.001])
xlabel('Channel');
ylabel('Time (s)');
title('cur - fk')
saveas(h7,'cur_fk.png');

% save('.mat', 'd_curvelet', 'd_fk2', 'd_bp');
save(filename(1:end-4), 'd_curvelet', 'd_fk2', 'd_bp');