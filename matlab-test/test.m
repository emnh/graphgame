function [] = mask(k)

if strcmp(class(k), 'char')
    k = sscanf(k, '%d');
end

a = mod(0:k^2-1, k)-(k-1)/2;
a = reshape(a, k, k);
b = a';

c = sqrt(a.^2 + b.^2);
maxd = c(1,1);
c = c / maxd;

rgb = reshape([c, c, c], k, k, 3);

%imwrite(rgb, 'test.png', 'png');
