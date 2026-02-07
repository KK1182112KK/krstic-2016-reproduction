%% STARTUP  Auto-configure MATLAB path for this project
%  MATLAB runs this automatically when you cd to this directory.

root = fileparts(mfilename('fullpath'));
addpath(genpath(fullfile(root, 'src')));
addpath(fullfile(root, 'tests'));

fprintf('Bekiaris-Liberis & Krstic (2016) — paths configured.\n');
fprintf('  run_all        — reproduce all results\n');
fprintf('  run_all(''test'') — run validation tests\n');
clear root;
