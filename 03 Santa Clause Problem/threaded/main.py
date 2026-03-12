from lib import HR
import multiprocessing as mp

def main():
    north_pole = HR.HR(num_elves=18, num_reindeers=9)
    north_pole.simulate()

if __name__ == "__main__":
    mp.set_start_method("fork", force=True)
    main()