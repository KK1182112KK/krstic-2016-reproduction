function [t,X,U,Z,info] = run_original_dde(D,dt,t_end,X0,history_value,method)
% RUN_ORIGINAL_DDE Original plant (2016 Eqs. 28-29) + causal sampled feedback.
% No transport PDE, target-state integration, or future physical state.
% U is explicitly zero-order held between controller samples; this is not an
% exact implementation of the paper's continuous-time controller. Refine dt.
% D is never rounded. Steps split at delayed command switch times.
% Predictor (33-34) is reconstructed from X and the actual strict input history.
% Default RK4 integrates the literal physical RHS. 'exact-held' provides an
% independent original-plant flow check for the SAME held-input controller.
    if nargin<1 || isempty(D), D=1; end
    if nargin<2 || isempty(dt), dt=.01; end
    if nargin<3 || isempty(t_end), t_end=20; end
    if nargin<4 || isempty(X0), X0=[1;1]; end
    if nargin<5 || isempty(history_value), history_value=0; end
    if nargin<6 || isempty(method), method='rk4'; end
    validateattributes(D,{'numeric'},{'scalar','real','finite','nonnegative'});
    validateattributes(dt,{'numeric'},{'scalar','real','finite','positive'});
    validateattributes(t_end,{'numeric'},{'scalar','real','finite','positive'});
    validateattributes(X0,{'numeric'},{'numel',2,'real','finite'});
    validateattributes(history_value,{'numeric'},{'scalar','real','finite'});
    if ~any(strcmp(method,{'rk4','exact-held'})), error('Invalid plant method.'); end
    n=ceil(t_end/dt); t=min((0:n)'*dt,t_end);
    X=zeros(n+1,2); X(1,:)=X0(:)'; Z=zeros(n+1,2);
    U=zeros(n+1,1); Ud=zeros(n+1,1);
    for k=1:n+1
        % U(k) has NOT been written when this predictor is computed.
        Z(k,:)=history_predictor(t(k),X(k,:),D,t(1:k-1),U(1:k-1),history_value);
        U(k)=-Z(k,1)-2*Z(k,2);
        % Compare arrival timestamps directly; (t_j+D)-D may round below t_j.
        % No tolerance is added: a command must never be reported early.
        active=find(t(1:k)+D<=t(k),1,'last');
        if isempty(active), Ud(k)=history_value; else, Ud(k)=U(active); end
        if any(~isfinite([Z(k,:),U(k)])), error('Nonfinite controller; no clipping.'); end
        if k==n+1, break; end
        switches=t(1:k)+D;
        cuts=[t(k); switches(switches>t(k) & switches<t(k+1)); t(k+1)];
        y=X(k,:)';
        for j=1:numel(cuts)-1
            h=cuts(j+1)-cuts(j);
            ud=held((cuts(j)+cuts(j+1))/2-D,t(1:k),U(1:k),history_value);
            if strcmp(method,'exact-held')
                a=1/(1+ud^2); e1=expm1(a*h);
                y=[y(1)+2*(y(2)+ud)*e1/a-2*ud*h+U(k)*h; y(2)+(y(2)+ud)*e1];
            else
                k1=physical_rhs(y,U(k),ud);
                k2=physical_rhs(y+h*k1/2,U(k),ud);
                k3=physical_rhs(y+h*k2/2,U(k),ud);
                k4=physical_rhs(y+h*k3,U(k),ud);
                y=y+h*(k1+2*k2+2*k3+k4)/6;
            end
        end
        if any(~isfinite(y)), error('Nonfinite physical plant; no clipping.'); end
        X(k+1,:)=y';
    end
    z0=Z(1:end-1,:); z1=Z(2:end,:); u=U(1:end-1);
    f0=[2*z0(:,2)+u,(z0(:,2)+u)./(1+u.^2)];
    f1=[2*z1(:,2)+u,(z1(:,2)+u)./(1+u.^2)];
    info=struct('D',D,'sample_dt',dt,'history_value',history_value,...
        'plant_method',method,'U_delayed',Ud,'physical_state_dimension',2,...
        'controller','sampled, zero-order held; not ideal continuous-time',...
        'identity_residual',(z1-z0)./diff(t)-(f0+f1)/2);
end

function f=physical_rhs(x,u,ud)
    % Original Eqs. (28)-(29): delay is not substituted away.
    f=[2*x(2)+u; (x(2)+ud)/(1+ud^2)];
end

function u=held(q,times,values,prehistory)
    if q<0, u=prehistory; return; end
    i=find(times<=q,1,'last');
    if isempty(i), error('Missing causal input history.'); end
    u=values(i); % Issued command holds until the next sample; no extrapolation.
end

function z=history_predictor(t,x,D,times,values,prehistory)
    if D==0, z=x; return; end
    if ~isempty(times) && times(end)>t+1e-12, error('Future input sample.'); end
    lo=t-D;
    cuts=[lo;times(times>lo & times<t);t];
    widths=diff(cuts); mids=(cuts(1:end-1)+cuts(2:end))/2;
    u=prehistory*ones(size(widths));
    mask=mids>=0;
    if any(mask)
        if isempty(times), error('Missing predictor input history.'); end
        bins=discretize(mids(mask),[times;inf]);
        if any(isnan(bins)), error('Uncovered predictor interval.'); end
        u(mask)=values(bins);
    end
    a=1./(1+u.^2); ah=a.*widths; prefix=[0;cumsum(ah)];
    if prefix(end)>700, error('Predictor exponential overflow.'); end
    inc=u.*expm1(ah).*exp(-prefix(2:end)); accum=[0;cumsum(inc)];
    p2left=exp(prefix(1:end-1)).*(x(2)+accum(1:end-1));
    p2end=exp(prefix(end))*(x(2)+accum(end));
    p1end=x(1)+2*sum((p2left+u).*expm1(ah)./a-u.*widths);
    z=[p1end,p2end];
end
