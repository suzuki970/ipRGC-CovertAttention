

%%

for iProj = [SCREEN_YELLOW SCREEN_BLUE]
%#### yellow
Screen('SelectStereoDrawBuffer', windowPtr, iProj);
Screen('CopyWindow', window_light0.(['Pattern' num2str(iPattern)]).(['proj' num2str(iProj)]), windowPtr);


Screen('DrawLines', windowPtr, FixationXY, 2, cfg.LUMINANCE_TEXT);
end

%#### blue
% Screen('SelectStereoDrawBuffer', windowPtr, SCREEN_BLUE);
% Screen('CopyWindow', window_light0.(['Pattern' num2str(iPattern)]).proj2, windowPtr);


Screen('DrawingFinished', windowPtr);
Screen('Flip', windowPtr);


if useEyelink
    Eyelink('Message', 'onset_fixation');
end
        

timer.present = tic;
while 1
    if toc(timer.present) > cfg.TIME_FIXATION
        break;
    end
    clear keyCode;
    [keyIsDown,secs,keyCode]=KbCheck;
    if (keyCode(cfg.key.KEY_ESCAPE))  % interrupt by ESC
        Screen('CloseAll');
        Screen('ClearAll');
        ListenChar(0);
        sca;
        return
    end
end
