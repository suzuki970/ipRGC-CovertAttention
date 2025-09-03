%% Instruction

for i = 1:3
    
    for iProj = [SCREEN_NUMBER0 SCREEN_NUMBER1]
        Screen('SelectStereoDrawBuffer', window, iProj);
        texture = Screen('MakeTexture',window,image.(['instruction' num2str(i)]));
        Screen('DrawTexture', window, texture, [], rect);
    end
    Screen('DrawingFinished', window);
    Screen('Flip', window);


    KbQueueFlush;
    while 1
        [pressed, firstPress, firstRelease, lastPress, lastRelease]= KbQueueCheck();
        if firstPress(KbName('space')) > 0
            % Screen('DrawTexture', window, targetInd,[],rect);
            % Screen('Flip', window);
            break;
        end
        clear keyCode;
        [keyIsDown,secs,keyCode] = KbCheck;
        if (keyCode(cfg.key.KEY_ESCAPE))
            Screen('CloseAll');
            Screen('ClearAll');
            ListenChar(0);
            sca;
            return
        end
    end
end

if IsOSX
    Screen('TextFont', window, 'Hiragino Mincho Pro');
end

if Screen('Preference', 'TextRenderer') == 1
    if 1
        Screen('TextFont', window, '-:lang=ja');
    else
        Screen('TextFont', window, '-:lang=he');
        unicodetext = 1488:1514;
    end
end

for i = 1:5
    time.sec = tic;

    while toc(time.sec) < 1
        for iProj = [SCREEN_NUMBER0 SCREEN_NUMBER1]
            Screen('SelectStereoDrawBuffer', window, iProj);

%             if 1-toc(time.sec) < 0
%                 Screen('TextSize', window, 0   );
%             else
%                 Screen('TextSize', window, round(elSize.FONT_TITLE*(1-toc(time.sec))));
%             end
%             disp( round(elSize.FONT_TITLE*(1-toc(time.sec))))
%             Screen('TextSize', window,20);
%             Screen('TextSize', window, round(elSize.FONT_TITLE));
%             DrawFormattedText(window, myText,  tmp_rect(3)+elSize.SPACE, elSize.SPACE*1.5, [0,0,0],[],[],[],1.2);

            DrawFormattedText(window, num2str(i),'center','center',[0,0,0]);
        end

        Screen('DrawingFinished', window);
        Screen('Flip', window);

    end
end