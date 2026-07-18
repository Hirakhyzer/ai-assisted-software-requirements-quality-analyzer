function plot_requirements_metrics(outputDir)
% Plot synthetic requirements quality metrics from generated CSV files.
if nargin < 1
    outputDir = 'outputs';
end

summaryPath = fullfile(outputDir, 'results', 'synthetic_module_quality_summary.csv');
scoresPath = fullfile(outputDir, 'results', 'synthetic_requirement_quality_scores.csv');

modules = readtable(summaryPath);
scores = readtable(scoresPath);

figure;
bar(modules.mean_quality_index);
set(gca, 'XTickLabel', modules.module);
xtickangle(30);
ylabel('Mean quality index');
title('Requirement quality by module');

figure;
histogram(scores.requirement_quality_index);
xlabel('Requirement quality index');
ylabel('Count');
title('Requirement quality distribution');
end
