# imports
import math
import scipy.stats as st

def conf_int(mean, var, n, p=0.95):
    """
    Calculate a confidence interval
    :param mean: mean of simulations
    :param var: variance of simulations
    :param n: amount of simulations
    :param p: certainty percentage
    :return:
    """
    pnew = (p+1)/2
    zval = st.norm.ppf(pnew)
    sigma = math.sqrt(var)
    alambda = (zval*sigma)/math.sqrt(n)
    min_lambda = mean - alambda
    plus_lambda = mean + alambda
    return f"Confidence interval: [{min_lambda:.4f} < X < {plus_lambda:.4f}] with p = {p}"

def calc_rho(mu, lbda, c):
    return lbda/(c*mu)


def pwait(c, rho):
    """
    Probability that a job has to wait
    :param c: amount of servers
    :param rho: occupation rate per server
    :return: probability
    """
    fixed = ((c*rho)**c)/math.factorial(c)

    sum = 0
    for n in range(c):
        sum += ((c*rho)**n)/math.factorial(n)

    return fixed/((1-rho)*sum + fixed)


def expw(mu, c, rho):
    """
    Expected waiting time
    :param mu: server processing time
    :param c: amount of servers
    :param rho: occupation rate per server
    :return: Exp. waiting time
    """

    piw = pwait(c, rho)
    return piw * (1/(1-rho)) * 1/(c*mu)

def expquel(c, rho):
    """
    Expected queue length
    :param c: amount of servers
    :param rho: occupation rate per server
    :return: Exp. queue length
    """
    piw = pwait(c, rho)
    return piw * (rho/(1-rho))


# print(f'Probability that a job has to wait: {pwait(c, rho):.2f}')
# print(f'Expected waiting time E(W): {expw(mu, c, rho):.2f} time units')
# print(f'Expected queue length E(Lq): {expquel(c, rho):.2f} customers')
# print dataframe with data
# print(data)
# run_data.loc[round(SIM_TIME/5)] = [rho, SIM_TIME, data["AVG_WAITING"].mean()]
# print(f'Expected waiting time E(W): {expw(MU, SERVERS, RHO):.3f} time units')
# print(f'AVG waiting: {data["AVG_WAITING"].mean():.3f} time units')
# print(conf_int(data["AVG_WAITING"].mean(), data["AVG_WAITING"].var(), SIMULATIONS, p=0.95))
# print()
# print(f'AVG arriving: {data["AVG_ARRIVING"].mean():.3f} per time unit')
# print(conf_int(data["AVG_ARRIVING"].mean(), data["AVG_ARRIVING"].var(), SIMULATIONS, p=0.95))
# print()
# print(f'AVG leaving: {data["AVG_LEAVING"].mean():.3f} per time unit')
# print(conf_int(data["AVG_LEAVING"].mean(), data["AVG_LEAVING"].var(), SIMULATIONS, p=0.95))
# print(f'Simulation {s+1}')
# print(f'Average waiting time: {avg_waiting:.3f} time units')
# print(f'Avg customers arriving per time unit: {avg_arrivals:.3f} time units')
# print(f'Avg customers leaving per time unit: {avg_leavers:.3f} time units\n')

# print("EXPECTED VALUES AND PROBABILITIES")
#
# print(f'Rho: {RHO}\nMu: {MU}\nLambda: {LAMBDA}\nExpected interarrival time: {1 / LAMBDA:.2f} time units')
# print(f'Expected processing time per server: {1 / MU:.2f} time units\n')
# print(f'Probability that a job has to wait: {pwait(SERVERS, RHO):.2f}')
# print(f'Expected waiting time E(W): {expw(MU, SERVERS, RHO):.2f} time units')
# print(f'Expected queue length E(Lq): {expquel(SERVERS, RHO):.2f} customers\n')
