from numpy import sqrt as _sqrt

def CalculateTwissFromSigmaMatrix(sigma_matrix) :

    eps_x = _sqrt(sigma_matrix[0,0]*sigma_matrix[1,1] - sigma_matrix[0,1]*sigma_matrix[1,0])
    bet_x = sigma_matrix[0,0] / eps_x
    alp_x = sigma_matrix[0,1] / (eps_x * bet_x)
    gam_x = sigma_matrix[1,1] / eps_x - alp_x**2 / bet_x

    eps_y = _sqrt(sigma_matrix[2,2]*sigma_matrix[3,3] - sigma_matrix[2,3]*sigma_matrix[3,2])
    bet_y = sigma_matrix[2,2] / eps_y
    alp_y = sigma_matrix[2,3] / (eps_y * bet_y)
    gam_y = sigma_matrix[3,3] / eps_y - alp_y**2 / bet_y

    return {'eps_x':eps_x, 'bet_x':bet_x, 'alp_x':alp_x, 'gam_x':gam_x,
            'eps_y':eps_y, 'bet_y':bet_y, 'alp_y':alp_y, 'gam_y':gam_y}
