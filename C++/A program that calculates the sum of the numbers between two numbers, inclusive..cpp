#include <bits/stdc++.h>
using namespace std;
int main()
{
    int n, m, k;
    cin >> m >> n;
    k = 0;
    while (true)
    {
    	k = k + m;
        m++;
        if (m > n) break;
    }
    cout << k;
}
