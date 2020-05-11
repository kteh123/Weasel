function T1_map_final = T1Fitting(im_selected, TI)
	%% null point selection - at the moment everything below lowest val is negative; this can be changed based on the lowest error calculation 
	k = 1;
	for i = 1:length(im_selected(:,:,1))
		for j = 1:length(im_selected(1,:,1))
         
		[row,col] = find(im_selected(i,j,:)==min(im_selected(i,j,:))); % locate the null point of inversion
		ydata_neg = im_selected(i,j,1:col-1);  % read data from null point onwards
		ydata_pos = im_selected(i,j,col:end);  % read data from null point onwards
		ydata_neg_final(1,:) = ydata_neg(1,1,:);
		ydata_pos_final(1,:) = ydata_pos(1,1,:);
		ydataTot(k,:) = [-ydata_neg_final, ydata_pos_final];
		k = k+1;
		clear ydata_neg_final clear ydata_pos_final
      
		end
	end

	%% original non-linear curve fitting
	x0 = [max(im_selected(:)) max(im_selected(:))-min(im_selected(:)) 50]; % initial values for the a,b and T1 apparent
	lb = [0 -Inf 0]; % lower bound
	ub = [Inf Inf 3000]; % upper bound

	opts = optimset('Algorithm', 'levenberg-marquardt');
	t1_fitting = @(T1_apparent,TE)T1_apparent(1)-T1_apparent(2).*exp(-TI./T1_apparent(3)); % a-b*exp(-t/T1); % molli fitting
	for i = 1:length(im_selected(1,:,1))*length(im_selected(:,1,1))
		[T1_apparent(i,:),resnormbad,~,exitflagbad,outputbad] = lsqcurvefit(t1_fitting,x0,TI',ydataTot(i,:)',lb,ub,opts);
	end
	   
	%% Final T1 values: estimated T1 map from T1 apparent
	for i = 1:length(T1_apparent)
		T1_estimated(i,:) = T1_apparent(i,3).*((T1_apparent(i,2))./(T1_apparent(i,1))-1);%T1_estimated((B/A)-1) MOLLI scheme
	end

	%% Final T1 values
	T1_map_final = zeros(size(im_selected,1),size(im_selected,2),1); % empty matrix for T1 estimated
	k=1;
	for i = 1:length(im_selected(1,:,1))
		for j = 1:length(im_selected(:,1,1))
			T1_map_final(i,j) = T1_estimated(k);%% 
			k=k+1;
			
		end
	end
end
