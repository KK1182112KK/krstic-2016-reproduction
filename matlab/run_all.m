function run_all(mode)
% RUN_ALL Default: original physical plant + causal sampled predictor.
% run_all          : direct simulation, refinement and figures
% run_all('sim')   : direct simulation and refinement, no figures
% run_all('fig')   : rerun direct simulation and generate figures
% run_all('test')  : tests only
% run_all('all')   : direct simulation, figures, tests
% run_all('legacy-pde'): explicitly run the old transport-PDE approximation
    if nargin<1, mode='default'; end
    root=fileparts(mfilename('fullpath'));
    addpath(genpath(fullfile(root,'src')));
    if strcmpi(mode,'test'), run_tests(root); return; end
    if strcmpi(mode,'legacy-pde')
        fprintf('LEGACY: upwind transport-PDE approximation, not direct delay lookup.\n');
        run_full_closedloop(1,100,20,[1;1]); return;
    end
    if ~any(strcmpi(mode,{'default','sim','fig','all'}))
        error('Unknown mode. Use sim, fig, test, all, or legacy-pde.');
    end
    out=fullfile(root,'results','direct-dde');
    if ~exist(out,'dir'), mkdir(out); end
    hs=[.02,.01,.005]; rows=zeros(numel(hs),4); previous=[];
    for j=1:numel(hs)
        [t,X,U,Z,info]=run_original_dde(1,hs(j),20,[1;1]);
        change=NaN;
        if ~isempty(previous)
            fine=interp1(t,X,previous.t,'linear');
            change=max(abs(fine(:)-previous.X(:)));
        end
        rows(j,:)=[hs(j),norm(X(end,:)),max(abs(info.identity_residual(:))),change];
        previous=struct('t',t,'X',X);
    end
    fprintf('Original Eqs. 28-29; only X is propagated; Z is reconstructed.\n');
    fprintf('Controller: sampled/ZOH. Refinement is required; no ideal-feedback claim.\n');
    summary=array2table(rows,'VariableNames',{'sample_dt','final_X_norm',...
        'max_identity_residual','change_from_coarser_X'});
    disp(summary); writetable(summary,fullfile(out,'refinement.csv'));
    writetable(array2table([t,X,U,Z,info.U_delayed],'VariableNames',...
        {'t','X1','X2','U','Z1','Z2','U_delayed'}),fullfile(out,'trajectory.csv'));
    save(fullfile(out,'direct_run.mat'),'t','X','U','Z','info');
    if ~strcmpi(mode,'sim')
        figure; plot(t,X); xlabel('Time'); ylabel('Physical state');
        legend('X1','X2'); title('Original delayed plant, sampled predictor feedback');
        saveas(gcf,fullfile(out,'physical_states.png'));
        figure; stairs(t,U); xlabel('Time'); ylabel('U'); title('Applied held input');
        saveas(gcf,fullfile(out,'control.png'));
        figure; semilogy(t(1:end-1),max(abs(info.identity_residual),[],2)+eps);
        xlabel('Time'); ylabel('Normalized integral defect');
        title('Postprocessed transformation identity diagnostic');
        saveas(gcf,fullfile(out,'identity_residual.png'));
    end
    if strcmpi(mode,'all'), run_tests(root); end
end

function run_tests(root)
    results=runtests(fullfile(root,'tests'),'IncludeSubfolders',true);
    disp(results);
    if any([results.Failed]), error('MATLAB test failure.'); end
end
