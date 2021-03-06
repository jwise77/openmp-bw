#include "error.def"

      subroutine wrapper2d(x, rank, n1, n2, n3, dir, method)

      implicit none

      integer :: rank, n1, n2, n3, dir
      complex :: x(n1,n2)
      external :: method

      complex, allocatable :: y(:,:)
      integer :: n(3)
      integer :: i,j

      if( rank /= 2 ) then
        write(0,*) '2D wrapper rank != 2'
        ERROR_MESSAGE
      end if

      if( n3 /= 1 ) then
        write(0,*) '2D wrapper dim3 > 1'
        ERROR_MESSAGE
      end if

      n(1) = n1
      n(2) = 1
      n(3) = 1

      do j=1,n2
      call fftwrap2d( x(1,j), n, dir, method )
      end do

      allocate( y(n2,n1) )

      call rotate2d(x,n1,n2,y)

      n(1) = n2
      do i=1,n1
      call fftwrap2d( y(1,i), n, dir, method )
      end do

      call rotate2d(y,n2,n1,x)

      deallocate( y )

      return

      end


      subroutine fftwrap2d( a, n, dir, method )

      implicit none

      complex :: a(*)
      integer :: n(3)
      integer :: dir
      external :: method

      call method(a, n(1), dir)

      return

      end
