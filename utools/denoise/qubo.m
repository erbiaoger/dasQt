[n1,n2]=size(DS04);
t=[0:n1]*0.00000001;
x=1:n2;
tic
is_real=1;           % Type of the transform(0: complex-valued curvelets,1: real-valued curvelets)
finest=1;            % Chooses one of two possibilities for the coefficients at the finest level(1: curvelets,2: wavelets)
alpha=3;           % Tresholding parameter
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
    
%Cdn=fdct_wrapping(StrainRate55,is_real,finest);     %
Cdn=fdct_wrapping(DS04,is_real,finest);

Smax=length(Cdn);
Sigma0=alpha*median(median(abs(Cdn{Smax}{1})))/0.58;     % 原参数0.58 
Sigma=Sigma0;
sigma=[Sigma,linspace(2.5*Sigma,0.5*Sigma,niter)];
Sigma=sigma(1);

%Cdn=fdct_wrapping(dsbg,is_real,finest);     %
Cdn=fdct_wrapping(d_bp,is_real,finest); 
    
    Ct=Cdn;
    for s=2:length(Cdn)
        thresh=Sigma+Sigma*s;
        for w=1:length(Cdn{s})
            Ct{s}{w}=Cdn{s}{w}.*(abs(Cdn{s}{w})>thresh*E{s}{w});
        end
    end
    
d_curvelet=real(ifdct_wrapping(Ct,is_real,n1,n2));
toc