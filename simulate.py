from ast import Or
from tracemalloc import start
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import copy
import random
import math
import scipy.stats as st
from probabilities import *
from collections import Counter

chunksize = 1000
days = list(range(1, 23))

lambda_data_2048 = {
        'mobilenet_v2': 43.6,
        'inception_v3': 275.5,
        'resnet50': 193,
        'vgg16': 466,
        'vgg19': 554,
    }

models = list(lambda_data_2048.keys())
print(models)

for model in models:
    for day in days:
        twitter_datas = pd.read_csv(f"datetime-csv/202211{day:02d}.csv", chunksize = chunksize)
        twitter_datas = list(twitter_datas)
        twitter_datas = twitter_datas[0]
        twitter_datas.columns = ['Time', 'QPS']
        perform_datas = pd.read_csv("perform.csv")
        # pd.options.display.float_format = '{:.10f}'.format


        
        lambda_price_2048 = 0.0000000333


        inferentia_price = 0.0060333333 / 60

        datas = twitter_datas

        x = list(datas.get('Time').values)
        y = list(datas.get('QPS').values)

        print(datas['QPS'][:chunksize].sum())

        totals = datas['QPS'][:chunksize].sum()

        TARGET_LATENCY = 200  # ms
        T = [1, 5, 10, 30, 60, 180]

        default = {}
        for t in T:
            default[t] = 0

        inferentia_price = 0.000100555555

        model_index = {
            "mobilenet_v2": 0,
            "inception_v3": 1,
            "resnet50": 2,
            "vgg16": 3,
            "vgg19": 4
        }

        df = perform_datas[perform_datas["models"].isin([model])]
        inferentia_per_second = int(df['InferentiaPerform'].values[0] / 60)
        lambda_per_second = int(df['LambdaPerform'].values[0] / 60)

        lambda_per_price = float(df['LambdaEventPerPrice'].values[0])

        PerformInferentia = copy.deepcopy(default)
        for t in T:
            PerformInferentia[t] = inferentia_per_second * t

        PerformLambda = copy.deepcopy(default)
        for t in T:
            PerformLambda[t] = lambda_per_second * t

        # print("Perform_Inferentia:", PerformInferentia)
        # print("Perform_Lambda:", PerformLambda)

        InferentiaInstances = 0
        InferentiaJobs = 0
        LambdaWorkers = 0

        Instance_Cold_Start = 10
        EVENT_TESTING = 1

        WorkedByLambda = []
        WorkedByInferentia = []


        # Time Step 별 도착하는 Event 양 체크
        def RequestMonitor(start_time):
            requests = copy.deepcopy(default)
            for t in T:
                # 현재 시간 부터 앞으로의 t 만큼 체크, 이벤트의 총합 계산
                requests[t] = twitter_datas[
                    start_time:start_time + t]['QPS'].values.sum(axis=0) * EVENT_TESTING
            return requests


        start_time = 0
        end_time = chunksize - 1

        instance_start_time = 0
        SIMULATIONS = 1
        InstanceOnTimes = 0


        def OnlyLambda(currentJobs, events):
            currentJobs += events[0]
            return currentJobs


        def MaxInstance(NeedInstances, events):
            while events[0] > inferentia_per_second * NeedInstances:
                NeedInstances += 1

            return NeedInstances


        def ScalingInstances(UsedInstances, events):
            instances = 0
            while True:
                RemainEvents = events - \
                    np.array(list(PerformInferentia.values())) * (instances + 1)
                EventRatio = len(RemainEvents[RemainEvents < 0]) / len(RemainEvents)
                if EventRatio > 0.5:
                    break
                else:
                    instances += 1

            instances += 1
            UsedInstances += instances
            return UsedInstances


        def OptimizeSystem(LambdaJobs, InferentiaInstances, events):
            CurrentLambdaJobs = 0
            TotalEventValues = events
            NeedInstances = 0
            while True:
                RemainEvents = TotalEventValues - \
                    np.array(list(PerformInferentia.values())) * (NeedInstances + 1)
                EventRatio = len(RemainEvents[RemainEvents < 0]) / len(RemainEvents)
                if EventRatio > 0.5:
                    break
                else:
                    NeedInstances += 1

            if NeedInstances == 0:
                RemainEvents = TotalEventValues
            else:
                RemainEvents = TotalEventValues % (
                    NeedInstances * np.array(list(PerformInferentia.values())))

            PreferedLambda = np.array(list(PerformLambda.values())) > RemainEvents
            LambdaRatio = len(
                PreferedLambda[PreferedLambda == True]) / len(PreferedLambda)
            #     print("LambdaRatio:", LambdaRatio)

            LambdaUsed = False
            if LambdaRatio <= 0.5:
                NeedInstances += 1
            else:
                LambdaUsed = True

            CurrentInferentiaJobs = events[0]

            # if InferentiaInstances > 0:
            #     time_idx = 0
            #     for TimeKey, SIM_TIME in PerformInferentia.items():
            #         SERVERS = NeedInstances
            #         MU = SIM_TIME / TimeKey  # 1/mu is exponential service times
            #         LAMBDA = TotalEventValues[time_idx] / TimeKey
            #         RHO = LAMBDA / (MU * SERVERS)

            #         W = expw(MU, SERVERS, RHO) / 2 + 1 / MU
                    #             print("SIM_TIME:",SIM_TIME)
                    #             print("EXPECTED VALUES AND PROBABILITIES")

                    #             print(f'Rho: {RHO}\nMu: {MU}\nLambda: {LAMBDA}\nExpected interarrival time: {1 / LAMBDA:.5f} time units')
                    #             print(f'Expected processing time per server: {1 / MU:.5f} time units\n')
                    #             print(f'Probability that a job has to wait: {pwait(SERVERS, RHO):.5f}')
                    #             print(f'Expected queue length E(Lq): {expquel(SERVERS, RHO):.5f} customers\n')
                    #             print(f'Expected waiting time E(W): {W:.5f} time units\n')
                    #             E = expw(MU, SERVERS, RHO)

                    # time_idx += 1

            #             if W > TARGET_LATENCY / 1000:
            #                 LambdaUsed = True
            #                 CurrentLambdaJobs += int(TotalEventValues[0] / 2)
            #                 print("W:", W, "Violate Target Latency")

            if LambdaUsed:
                CurrentLambdaJobs = RemainEvents[0]

            CurrentInferentiaJobs = events[0] - CurrentLambdaJobs

            WorkedByLambda.append(CurrentLambdaJobs)
            WorkedByInferentia.append(CurrentInferentiaJobs)

            LambdaJobs += CurrentLambdaJobs
            InferentiaInstances += NeedInstances
            return LambdaJobs, InferentiaInstances


        def Oracle(LambdaJobs, InferentiaInstances, events):
            event = events[0]
            NeedInstances = event // PerformInferentia[1]
            remainEvents = event % PerformInferentia[1]

            if PerformLambda[1] < remainEvents:
                NeedInstances += 1
            else:
                LambdaJobs += remainEvents
            InferentiaInstances += NeedInstances
            return LambdaJobs, InferentiaInstances


        onlylambda_jobs = 0
        max_instances = 0
        scaling_usedinstances = 0
        optimizesystem_jobs = [0, 0]
        oracle_jobs = [0, 0]

        start_time = 0

        while (start_time <= end_time):
            remain_time = end_time - start_time
            last_time = T[-1]
            if last_time > remain_time:
                T = T[:-1]

            Events = RequestMonitor(start_time)

            TotalEventValues = np.array(list(Events.values()))

            onlylambda_jobs = OnlyLambda(onlylambda_jobs, TotalEventValues)
            max_instances = MaxInstance(max_instances, TotalEventValues)
            scaling_usedinstances = ScalingInstances(
                scaling_usedinstances, TotalEventValues)
            optimizesystem_jobs[0], optimizesystem_jobs[1] = OptimizeSystem(
                optimizesystem_jobs[0], optimizesystem_jobs[1], TotalEventValues)
            oracle_jobs[0], oracle_jobs[1] = Oracle(
                oracle_jobs[0], oracle_jobs[1], TotalEventValues)

            start_time += 1

        print(onlylambda_jobs,
            max_instances,
            scaling_usedinstances,
            optimizesystem_jobs,
            oracle_jobs)

        print(f'-------------------------------------{day:2d}-------------------------------------')
        data = {
            'Model': model,
            'Only Lambda': onlylambda_jobs * lambda_per_price,
            'Max Instances': max_instances * (end_time + 1) * inferentia_price,
            'Scaling Instances': scaling_usedinstances * inferentia_price,
            'Optimize System': optimizesystem_jobs[0] * lambda_per_price + optimizesystem_jobs[1] * inferentia_price,
            'Oracle': oracle_jobs[0] * lambda_per_price + oracle_jobs[1] * inferentia_price,
            'Case': model + '_' + str(day) # 모델 실행일 수에 대한 정보
        }

        with open('data.json', 'a') as f:
            json.dump(data, f)
            f.write(',')

        print('Model:', model)
        print('Only Lambda:', onlylambda_jobs * lambda_per_price)
        print('Max Instances:', max_instances * (end_time + 1) * inferentia_price)
        print('Scaling Instances:', scaling_usedinstances * inferentia_price)
        print('Optimize System:', optimizesystem_jobs[0] * lambda_per_price +
            optimizesystem_jobs[1] * inferentia_price)
        print('Oracle:', oracle_jobs[0] * lambda_per_price +
            oracle_jobs[1] * inferentia_price)
