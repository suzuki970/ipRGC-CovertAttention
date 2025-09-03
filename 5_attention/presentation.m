
tmp_cue = cfg.condition_frame.Cue(iTrial);
tmp_angle = cfg.condition_frame.Angle(iTrial);

if useEyelink
    Eyelink('Message', ['Condition_Cue ' num2str(tmp_cue)]);
    Eyelink('Message', ['Condition_Pattern ' num2str(iPattern)]);
    Eyelink('Message', ['Condition_Angle ' num2str(tmp_angle)]);
    
%     if iPattern == 1
%         Eyelink('Message', ['Condition_pattern_name flux_ipRGC']);
%     else
%         Eyelink('Message', ['Condition_pattern_name ipRGC_flux']);
%     end

end

if tmp_cue == 1
    disp('Cue: left');
else
    disp('Cue: right');
end

disp(['Screen: ' angleName{tmp_angle+1}]);



%% arrow screen

% for iProj = [SCREEN_YELLOW SCREEN_BLUE]
%     Screen('SelectStereoDrawBuffer', windowPtr, iProj);
%     Screen('CopyWindow', empty, windowPtr);
% end
% 
% Screen('DrawingFinished', windowPtr);
% Screen('Flip', windowPtr);

for iProj = [SCREEN_YELLOW SCREEN_BLUE]
    Screen('SelectStereoDrawBuffer', windowPtr, iProj);
    Screen('CopyWindow', window_light0.(['Pattern' num2str(iPattern)]).(['proj' num2str(iProj)]), windowPtr);
end

r = arrowLen/2;
x = r / cos(pi/4);
y = r / sin(pi/4);

if tmp_cue == 1 %#### left
    xy = [centerX-arrowLen, centerX+arrowLen,...
        centerX-arrowLen, centerX-arrowLen+x,...
        centerX-arrowLen, centerX-arrowLen+x; ...
        centerY, centerY,...
        centerY, centerY-y,...
        centerY, centerY+y];

    Screen('DrawLines', windowPtr, xy, 4, cfg.LUMINANCE_TEXT);
else %#### right
    xy = [centerX-arrowLen, centerX+arrowLen,...
        centerX+arrowLen, centerX+arrowLen-x,...
        centerX+arrowLen, centerX+arrowLen-x; ...
        centerY, centerY,...
        centerY, centerY-y,...
        centerY, centerY+y];

    Screen('DrawLines', windowPtr, xy, 4, cfg.LUMINANCE_TEXT);
end

Screen('DrawingFinished', windowPtr);
Screen('Flip', windowPtr);

if useEyelink
    Eyelink('Message', 'onset_arrow');
end

timer.present = tic;
while 1
    if toc(timer.present) > 0.5
        break;
    end
end


%% pre stimulus

% for iProj = [SCREEN_YELLOW SCREEN_BLUE]
%     Screen('SelectStereoDrawBuffer', windowPtr, iProj);
%     Screen('CopyWindow', empty, windowPtr);
% end
% 
% Screen('DrawingFinished', windowPtr);
% Screen('Flip', windowPtr);

for iProj = [SCREEN_YELLOW SCREEN_BLUE]
    Screen('SelectStereoDrawBuffer', windowPtr, iProj);
    Screen('CopyWindow', window_light0.(['Pattern' num2str(iPattern)]).(['proj' num2str(iProj)]), windowPtr);
end

Screen('DrawingFinished', windowPtr);
Screen('Flip', windowPtr);

if useEyelink
    Eyelink('Message', 'onset_prestim');
end

timer.present = tic;
while 1
    if toc(timer.present) > cfg.condition_frame.time(iTrial)
        break;
    end
end


%% target


for iProj = [SCREEN_YELLOW SCREEN_BLUE]
    Screen('SelectStereoDrawBuffer', windowPtr, iProj);
    Screen('CopyWindow', window_light.(['Pattern' num2str(iPattern)]).(angleName{tmp_angle+1}).(['proj' num2str(iProj)]), windowPtr);
end

Screen('DrawingFinished', windowPtr);
Screen('Flip', windowPtr);

% imageArray=Screen('GetImage', windowPtr);
% imwrite(imageArray, ['Trial' num2str(iTrial) '_Cue' num2str(tmp_cue) '_' angleName{tmp_angle+1} '.jpg']); 

timer.present = tic;

if useEyelink
    Eyelink('Message', 'onset_target');
end

timer.present = tic;
while 1
    if toc(timer.present) > 0.1
%     if toc(timer.present) > 20
        break;
    end

end

%% mask

% for iProj = [SCREEN_YELLOW SCREEN_BLUE]
%     Screen('SelectStereoDrawBuffer', windowPtr, iProj);
%     Screen('CopyWindow', empty, windowPtr);
% end
% 
% Screen('DrawingFinished', windowPtr);
% Screen('Flip', windowPtr);

for iProjNum = [SCREEN_YELLOW SCREEN_BLUE]
    Screen('SelectStereoDrawBuffer', windowPtr, iProjNum);
    Screen('CopyWindow', window_light.(['Pattern' num2str(iPattern)]).mask.(['proj' num2str(iProjNum)]), windowPtr);
end

if useEyelink
    Eyelink('Message', 'onset_mask');
end

Screen('DrawingFinished', windowPtr);
Screen('Flip', windowPtr);

%% Response

timer.present = tic;
while 1

    clear keyCode;
    [keyIsDown,secs,keyCode] = KbCheck;
    if (keyCode(cfg.key.KEY_ESCAPE))
        Screen('CloseAll');
        Screen('ClearAll');
        ListenChar(0);
        sca;
        return
    end

    if (keyCode(cfg.key.KEY_LEFT))
        cfg.res_summary.RT(iTrial,iPattern) = toc(timer.present);
        cfg.res_summary.res(iTrial,iPattern) = 0;
        if useEyelink
            Eyelink('Message', 'key_response 0');
        end
        
        disp('Key response: Left');
        break;
    end


    if (keyCode(cfg.key.KEY_RIGHT))
        cfg.res_summary.RT(iTrial,iPattern) = toc(timer.present);
        cfg.res_summary.res(iTrial,iPattern) = 1;
        if useEyelink
            Eyelink('Message', 'key_response 1');
        end
       
        disp('Key response: Right');
        break;
    end


end

%% post-stimulus

for iProjNum = [SCREEN_YELLOW SCREEN_BLUE]
    Screen('SelectStereoDrawBuffer', windowPtr, iProjNum);
    Screen('CopyWindow', window_light0.(['Pattern' num2str(iPattern)]).(['proj' num2str(iProjNum)]), windowPtr);
end

if useEyelink
    Eyelink('Message', 'onset_poststim');
end

Screen('DrawingFinished', windowPtr);
Screen('Flip', windowPtr);

timer.present = tic;

while 1
    if toc(timer.present) > 1
        break;
    end

end
