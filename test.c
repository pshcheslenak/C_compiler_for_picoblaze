#include <stdio.h>

void func1(){
        int a =20;
        int b = a + 30;
}

// // void func2(){
// //         int a= 10;
// //         int b =20;
// //         int c = a + b;
// //         func1(a);
// // }

// int main() {
//         // int a = 255;
//         // int b = 245;
//         // int result = 0;
//         // for (int i = 0; i < 5; i++) {
//         //         if (i > 3) {
//         //                 i += 2;
//         //         }
//                 // result += i;
//         // }
//         // int c;
//         // c = a + b;
//         // // printf("%d", c);
//         // if (3 > 4){
//                 func1();
//         // }
//         return 0;
// }


int main() {
        int result = 0;
        for (int i = 0; i < 5; i++) {
                result += i;
        }
        func1();
        return 0;
}