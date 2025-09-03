
%% Eyelink data
if useEyelink
    Eyelink('StopRecording');
    Eyelink('CloseFile');
    try
        fprintf('Receiving data file ''%s''\n', edfFile );
        status = Eyelink('ReceiveFile');
        if status > 0
            fprintf('ReceiveFile status %d\n', status);
        end
        if 2==exist(edfFile, 'file')
            fprintf('Data file ''%s'' can be found in ''%s''\n', edfFile, pwd );
        end
    catch rdf
        fprintf('Problem receiving data file ''%s''\n', edfFile );
        rdf;
    end
end

%% config
foobar = ['results/' cfg.participantsInfo.name];

if ~exist(foobar,'dir')
    mkdir(foobar);
end

% save([foobar save_name '_condition'], 'cfg', 'param');
save([foobar save_name '_condition'], 'cfg');

if useEyelink
    newFileName = split(edfFile,'.edf');
    newFileName = [newFileName{1} '_' now_time '_' num2str(iPattern) '.edf'];
    movefile(edfFile, [foobar '/' newFileName]);

    command = ['edf2asc ',[foobar '/' newFileName]];
    status = dos(command);

end
