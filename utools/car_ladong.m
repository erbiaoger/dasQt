load car.mat
dx=3.063;
dt=1e-3;
% aa(:,:)=data(2,:,:);
aa(:,:)=data(1,1:60000,21:100);
[nt,ng]=size(aa);


for i=1:ng
    aaa(:,i)=bp_filter(aa(:,i),dt,0.01,0.1,1,2);
end


figure
imagesc(aaa(:,:))
caxis([-0.1,0.1])
figure
imagesc(norm_trace(aaa));

vmin=-15;
vmax=15;
dv=0.1;
np=length(vmax:-dv:vmin);
fmin=0.01;
fmax=1;
df=0.01;
x=dx:dx:dx*ng;
uxt=norm_trace(aaa);
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
% for luoi=lf:nf
%  ml(:,luoi)=ml(:,luoi)./max(ml(:,luoi));
% end
 ml=ml(:,lf:nf);
 
 figure
 imagesc(fmin:df:fmax,(vmin:dv:vmax)*3.6,ml)
 colormap(jet)
 mn=sum(ml');
 [~,inxm]=max(mn);
 vv=(vmin:dv:vmax)*3.6;
 vv(inxm)
 figure
 plot(vv, mn);