/* 判定テーブル */
const uchar_t o_ucJudgeResult[AA][BB] = {
/* POS:両方①	*/	{	ABCD_MYSELF,		ABCD_MYSELF,		ABCD_MYSELF,		ABCD_MYSELF		},
/* POS:両方②	*/	{	ABCD_MYSELF,		ABCD_MYSELF,		ABCD_MYSELF,		ABCD_MYSELF		},

/* POS:上り①	*/	{	ABCD_MYSELF,		ABCD_NOT_MYSELF,	ABCD_MYSELF,		ABCD_NOT_MYSELF	},
/* POS:上り②	*/	{	ABCD_MYSELF,		ABCD_NOT_MYSELF,	ABCD_MYSELF,		ABCD_NOT_MYSELF	},

/* POS:下り①	*/	{	ABCD_NOT_MYSELF,	ABCD_MYSELF,		ABCD_NOT_MYSELF,	ABCD_MYSELF		},
/* POS:下り②	*/	{	ABCD_NOT_MYSELF,	ABCD_MYSELF,		ABCD_NOT_MYSELF,	ABCD_MYSELF		},
};

int a[][][][] = { 
    {
        {
            {1,2,3}, 
            {4,5,6}
        },
        {
            {11,12,13}, 
            {14,15,16}
        }
    },
    {
        {
            {101,102,103}, 
            {104,105,106},
            {104,105,106}
        },
        {
            {111,112,113}, 
            {114,115,116},
            {},
            {114,115,116}
        }
    }
};


static int one_dim_array[] = 
/* 一次元配列 */
{
	1,2,/*aaa*/,4	/* コメント */
};

/* 三次元配列 */
ABCDEFG b[2][2][] = { 
    {
        {1,2,3}, 
        {4,5,6}
    },
    {
        {11,12,13}, 
        {14,15,16,},
    }
};

const srv_matrix_t o_stMatrixJump_VoiceWhole[SRV_MATRIXJUMP_VOICEWHOLE_MAX] =
{
	{Srv_MtrxPrcesUndefinedState},			// 0x00 未定義
	{Srv_MtrxPrcesNop},						// 0x01 NOP
	{Srv_MtrxPrcesBcchInfoAllChUsed}, 		// 0x02
	{Srv_MtrxPrcesBcchInfo1ChUsed},			// 0x03
	{Srv_MtrxPrcesBcchInfo2ChUsed},			// 0x04
	{Srv_MtrxPrcesBcchInfoAllChUnUsed},		// 0x05
	{Srv_MtrxPrcesSyncOutCch},				// 0x06
	{Srv_MtrxPrcesOnHook},					// 0x07
	{Srv_MtrxPrcesOffHook},					// 0x08
	{Srv_MtrxPrcesFailureTemp},				// 0x09
	{Srv_MtrxPrcesFailureRecovery},			// 0x0a
};