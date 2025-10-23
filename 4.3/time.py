import time
import turtle

start = time.perf_counter_ns()
print(start)
# turtle.tracer(10e5)
# turtle.speed(0)
turtle.delay(0)
count = int(10e4)
for i in range(count):
	turtle.right(1)
	print(f"{(((i+1)/count)*100):.5f}%", end="\r")
end = time.perf_counter_ns()
print()
print(end)

print(f"FINISHED: {end - start}ns | {(end - start)/1e9}s")