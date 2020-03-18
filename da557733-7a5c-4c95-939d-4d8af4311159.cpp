#include <bits/stdc++.h>
using namespace std;
typedef  long long ll;
#define fr first
#define se second
#define pb push_back
typedef unsigned long long ull;

int main(int argc, char const *argv[])
{
	
	ios_base::sync_with_stdio(false);
    cin.tie(NULL);
	int t;
	cin>>t;
	while(t--){
		ull n,k;
		cin>>n>>k;
		ull a[n];
		for(int i=0 ; i<n ; i++){
			cin>>a[i];
		}
		map<int,int> taken;
		int flg =  1;
		for(int i=0 ; (i<n)&&flg ; i++) {
			ull val = a[i];
			ull pow = 0;
			while(val > 0){
				ull rem = val%k;
				if(rem != 0 && rem != 1){
					flg= 0;
					break;
				}
				if(rem != 0){
					if(taken[pow]){
						flg = 0;
						break;
					}else{
						taken[pow] = 1;
					}
				}
				val /= k;
				pow++;
			}
		}
		if(flg){
			cout<<"YES\n";
		}else{
			cout<<"NO\n";
		}
	}	
	

	return 0;
}