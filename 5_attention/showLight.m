
%%
fprintf('-------------- Light ON --------------\n')

Screen('SelectStereoDrawBuffer', windowPtr, SCREEN_YELLOW);
Screen('CopyWindow', window_light.(light_name{iLight}).proj1,windowPtr);

%% blue
Screen('SelectStereoDrawBuffer', windowPtr, SCREEN_BLUE);
Screen('CopyWindow', window_light.(light_name{iLight}).proj2,windowPtr);

Screen('DrawingFinished', windowPtr);

Screen('Flip', windowPtr);

if useEyelink
    Eyelink('Message', 'light_onset');
end
