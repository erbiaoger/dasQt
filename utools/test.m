
clear;clc

load norm_data.mat
dx=3.063;
dt=1e-3;
% aa(:,:)=data(2,:,:);
aa(:,:)=norm_data;
[nt,ng]=size(aa);



vmin=-15;
vmax=15;
dv=0.1;
np=length(vmax:-dv:vmin);
fmin=0.01;
fmax=1;
df=0.01;
x=dx:dx:dx*ng;
uxt=aa;
ccn=fix(1./df./dt);
d=fft(uxt,ccn);
d=d.';
lf=round(fmin./df)+1;
nf=round(fmax./df)+1;
pp=1./(vmin:dv:vmax)';
ll0=1i.*2.*pi.*df.*(pp*x);
mm=zeros(np,nf);


for luoj=lf:nf
l=exp(ll0.*(luoj-1));
mm(:,luoj)=(l*d(:,luoj));
end
ml=abs(mm);