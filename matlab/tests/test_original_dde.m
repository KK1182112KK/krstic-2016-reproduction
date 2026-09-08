function tests=test_original_dde
    tests=functiontests(localfunctions);
end
function testStartup(tc)
    [t,X,U,Z,info]=run_original_dde(.73,.01,.73,[1;1]);
    verifyEqual(tc,Z(1,:),[2*exp(.73)-1,exp(.73)],'AbsTol',1e-12);
    verifyEqual(tc,U(1),1-4*exp(.73),'AbsTol',1e-12);
    verifyLessThan(tc,max(abs(X(:,2)-exp(t))),2e-9);
    verifyEqual(tc,info.U_delayed(t<.73),zeros(sum(t<.73),1));
end
function testPhysicalFlow(tc)
    [~,X,U]=run_original_dde(.735,.01,2,[1;1],0,'rk4');
    [~,Xe,Ue]=run_original_dde(.735,.01,2,[1;1],0,'exact-held');
    verifyLessThan(tc,max(abs(X(:)-Xe(:))),5e-8);
    verifyLessThan(tc,max(abs(U(:)-Ue(:))),2e-7);
end
function testZero(tc)
    [~,X,U]=run_original_dde(1,.01,1,[0;0]);
    verifyEqual(tc,X,zeros(size(X))); verifyEqual(tc,U,zeros(size(U)));
end
function testHorizonIndependence(tc)
    [t,X,U]=run_original_dde(1,.01,.5,[1;1]);
    [~,XL,UL]=run_original_dde(1,.01,1,[1;1]);
    verifyEqual(tc,X,XL(1:numel(t),:)); verifyEqual(tc,U,UL(1:numel(t)));
end
