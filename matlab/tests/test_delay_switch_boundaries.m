function tests=test_delay_switch_boundaries
% Regression for right-continuous delayed-command diagnostic timestamps.
    tests=functiontests(localfunctions);
end
function testArrivalTimeOracle(tc)
    cases=[1,.01,3; .735,.01,1; 0,.01,.3; 2,.01,.3; .006,.01,.053];
    for prehistory=[0,-.4]
        for m=1:size(cases,1)
            D=cases(m,1);
            [t,~,U,~,info]=run_original_dde(D,cases(m,2),cases(m,3),[1;1],prehistory);
            expected=prehistory*ones(size(t));
            for k=1:numel(t)
                for j=1:k
                    if t(j)+D<=t(k), expected(k)=U(j); end
                end
            end
            verifyEqual(tc,info.U_delayed,expected);
        end
    end
end
function testKnownRoundoff(tc)
    [t,~,U,~,info]=run_original_dde(1,.01,1.2,[1;1]);
    j=find(t==.2,1);
    verifyEqual(tc,t(end),t(j)+1);
    verifyLessThan(tc,t(end)-1,t(j));
    verifyEqual(tc,info.U_delayed(end),U(j));
end
function testNoPrematureStartup(tc)
    D=1.2+eps(1.2);
    [t,~,~,~,info]=run_original_dde(D,.01,1.2,[1;1],-.4);
    verifyEqual(tc,info.U_delayed,-.4*ones(size(t)));
end
